from flask import Blueprint, jsonify, request
from app.product_models import list_products, create_product

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    return 'API ProdManager'


@main_bp.route('/produtos', methods=['GET'])
def get_products():
    products = list_products()
    return jsonify(products)


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
