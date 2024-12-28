from app.utils import db
from app.models.models import Product


def list_products():
    products = Product.query.all()
    result = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        }
        for product in products
    ]
    print("Products:", result)  # Debug print
    return result


def product_by_id(id_product):
    product = Product.query.get(id_product)
    if product:
        return {
            "id": product.id,
            "nome": product.name,
            "preco": product.price,
            "descricao": product.description
        }
    raise ValueError("Produto não encontrado.")


def create_product(data):
    try:

        if not data.get("name") or not data.get("price"):
            raise ValueError("O nome e o preço do produto são obrigatórios.")
        if data.get("price") > 0:

            new_product = Product(
                name=data.get("name"),
                price=data.get("price"),
                description=data.get("description")
            )

            db.session.add(new_product)
            db.session.commit()

            return new_product

        else:
            raise ValueError("O valor do produto deve ser positivo.")
    except Exception as e:
        db.session.rollback()
        print(f'Erro ao adicionar produto {e}')
        raise e


def update_product(id_product, new_data):
    product = Product.query.get(id_product)
    if not product:
        raise ValueError("Product not found!")

    print(f"Found product: {product}")

    product.name = new_data.get("name", product.name)
    product.price = new_data.get("price", product.price)
    product.description = new_data.get("description", product.description)

    db.session.commit()

    return product


def delete_product(id_product):
    product = Product.query.get(id_product)
    if not product:
        raise ValueError("Product not found!")
    try:
        db.session.delete(product)
        db.session.commit()
        return product
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting product: {e}")
        raise e
