# app/domain_services.py
from dataclasses import dataclass
from typing import Protocol


@dataclass
class ProductDTO:
    id: int | None
    name: str
    price: float
    description: str | None = None


class PriceRulesProvider(Protocol):

    def discount_for(self, product_name: str) -> float:
        ...


@dataclass
class PriceCalculator:
    rules: PriceRulesProvider

    def final_price(self, product: ProductDTO) -> float:
        d = self.rules.discount_for(product.name)
        d = max(0.0, min(d, 0.95))  # sanidade
        return round(product.price * (1.0 - d), 2)


class ProductRepo(Protocol):
    def next_id(self) -> int: ...
    def save(self, product: ProductDTO) -> ProductDTO: ...
    def get(self, pid: int) -> ProductDTO | None: ...


class Notifier(Protocol):
    def send(self, subject: str, body: str) -> None: ...


@dataclass
class CreateProductUseCase:
    repo: ProductRepo
    notifier: Notifier

    def execute(self, name: str, price: float,
                description: str | None = None) -> ProductDTO:
        product = ProductDTO(id=None, name=name,
                             price=price, description=description)
        product.id = self.repo.next_id()
        saved = self.repo.save(product)
        self.notifier.send(
            subject=f"Produto #{saved.id} criado",
            body=f"{saved.name} cadastrado por R$ {saved.price:.2f}"
        )
        return saved
