from flask import Blueprint, jsonify, request
from app.product_models import (
    list_products, create_product, update_product,
    delete_product, product_by_id
)
from app.models import Product

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    return 'API ProdManager'


@main_bp.route('/produtos', methods=['GET'])
def get_products():
    products = list_products()
    return jsonify(products)


@main_bp.route('/produtos/<int:id_product>', methods=["GET"])
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


@main_bp.route('/produtos', methods=["POST"])
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


@main_bp.route('/produtos/<int:id_product>', methods=["PUT"])
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


@main_bp.route('/produtos/<int:id_product>', methods=["DELETE"])
def delete_product_view(id_product):
    try:
        delete_product(id_product)
        return jsonify({"message": "Produto deletado com sucesso!"}), 200
    except ValueError as e:
        print(f"Delete error: {e}")
        return jsonify({"error": str(e)}), 404

