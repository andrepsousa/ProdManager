from typing import Dict, List, Optional
from app.utils import db
from app.models.models import Product


def _to_dict(p: Product) -> Dict:
    return {
        "id": p.id,
        "name": p.name,
        "price": float(p.price) if p.price is not None else None,
        "description": p.description,
    }


def list_products() -> List[Dict]:
    products = Product.query.all()
    result = [_to_dict(p) for p in products]
    # print("Products:", result)  # debug opcional
    return result


def product_by_id(id_product: int) -> Dict:
    product = Product.query.get(id_product)
    if not product:
        raise ValueError("Produto não encontrado.")
    return _to_dict(product)


def create_product(data: Dict) -> Dict:
    """
    Espera data com: name (str), price (num), description (str|None)
    Retorna o produto criado como dict.
    """
    name = (data.get("name") or "").strip()
    if not name:
        raise ValueError("O nome do produto é obrigatório.")

    try:
        price = float(data.get("price"))
    except (TypeError, ValueError):
        raise ValueError("Preço inválido.")

    if price <= 0:
        raise ValueError("O valor do produto deve ser positivo.")

    new_product = Product(
        name=name,
        price=price,
        description=data.get("description"),
    )
    try:
        db.session.add(new_product)
        db.session.commit()
        return _to_dict(new_product)
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao adicionar produto: {e}")
        raise


def update_product(id_product: int, new_data: Dict) -> Dict:
    product = Product.query.get(id_product)
    if not product:
        raise ValueError("Produto não encontrado.")

    if "name" in new_data:
        name = (new_data.get("name") or "").strip()
        if not name:
            raise ValueError("O nome do produto é obrigatório.")
        product.name = name

    if "price" in new_data:
        try:
            price = float(new_data.get("price"))
        except (TypeError, ValueError):
            raise ValueError("Preço inválido.")
        if price <= 0:
            raise ValueError("O valor do produto deve ser positivo.")
        product.price = price

    if "description" in new_data:
        product.description = new_data.get("description")

    db.session.commit()
    return _to_dict(product)


def delete_product(id_product: int) -> Dict:
    product = Product.query.get(id_product)
    if not product:
        raise ValueError("Produto não encontrado.")
    try:
        as_dict = _to_dict(product)  # útil para logs/retorno
        db.session.delete(product)
        db.session.commit()
        return as_dict
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao deletar produto: {e}")
        raise
