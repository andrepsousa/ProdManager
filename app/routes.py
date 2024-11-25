from flask import Blueprint, jsonify, request
from app.product_models import (
    list_products, create_product, update_product,
    delete_product, product_by_id
)
from app.user_models import register_user
from app.models import Product, User
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    return 'API ProdManager'


@main_bp.route('/produtos', methods=['GET'],
               endpoint='get_products')
def get_products():
    products = list_products()
    return jsonify(products)


@main_bp.route('/produtos/<int:id_product>', methods=["GET"],
               endpoint='get_products_id')
def get_products_id(id_product):
    try:
        product = product_by_id(id_product)
        return jsonify({
            "product": product
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@main_bp.route('/produtos', methods=["POST"],
               endpoint='create_product_view')
@jwt_required()
def create_product_view():
    try:

        data = request.get_json()
        new_product_data = {
            "name": data["name"],
            "price": data["price"],
            "description": data.get("description")
        }

        new_product = create_product(new_product_data)

        return jsonify({
            "message": "Produto criado com sucesso.",
            "product": {
                "id": new_product.id,
                "name": new_product.name,
                "price": new_product.price,
                "description": new_product.description
            }
        }), 201

    except KeyError as e:
        return jsonify({"error": f"Campo faltando na requisição: {str(e)}"}),
        400
    except Exception as e:
        return jsonify({"error": f"Erro ao criar o produto: {str(e)}"}), 500


@main_bp.route('/produtos/<int:id_product>', methods=["PUT"],
               endpoint='update_product_view')
@jwt_required()
def update_product_view(id_product):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body."}), 400

    try:
        updated_product = update_product(id_product, data)
        return jsonify({
            "message": "Product updated successfully.",
            "product": {
                "id": updated_product.id,
                "name": updated_product.name,
                "price": updated_product.price,
                "description": updated_product.description
            }
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Error updating product: {str(e)}"}), 500


@main_bp.route('/produtos/<int:id_product>', methods=["DELETE"],
               endpoint='delete_product_view')
@jwt_required()
def delete_product_view(id_product):
    try:
        delete_product(id_product)
        return jsonify({"message": "Produto deletado com sucesso!"}), 200
    except ValueError as e:
        print(f"Delete error: {e}")
        return jsonify({"error": str(e)}), 404


@main_bp.route('/cadastro', methods=["POST"],
               endpoint='register_view')
@jwt_required()
def register_view():
    data = request.get_json()
    try:
        user = register_user(
            username=data["username"],
            password=data["password"],
            email=data["email"]
        )
        return jsonify({"message": "Usuario registrado com sucesso!"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Erro inesperado: {str(e)}"}), 500


@main_bp.route('/login', methods=["POST"],
               endpoint='login')
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get("username")).first()
    if user and user.check_password(data.get("password")):
        access_token = create_access_token(
            identity=str(user.username))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Credenciais invalidas"}), 401
