from app import db
from app.models import Product


def list_products():
    products = Product.query.all()
    return [
        {
            "id": product.id,
            "nome": product.name,
            "preco": product.price,
            "descricao": product.description
        }
        for product in products
    ]


def create_product(data):
    try:

        if not data.get("name") or not data.get("price"):
            raise ValueError("O nome e o preço do produto são obrigatórios.")

        new_product = Product(
            name=data.get("name"),
            price=data.get("price"),
            description=data.get("description")
        )

        db.session.add(new_product)
        db.session.commit()

        return new_product
    except Exception as e:
        db.session.rollback()
        print(f'Erro ao adicionar produto {e}')
        raise e
    