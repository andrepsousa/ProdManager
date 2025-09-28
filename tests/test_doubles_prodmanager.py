import math
from app.domain_services import (
    ProductDTO, PriceCalculator, PriceRulesProvider,
    CreateProductUseCase, ProductRepo, Notifier
)


class PriceRulesStub(PriceRulesProvider):
    def __init__(self, fixed_rules: dict[str, float]):
        self.rules = fixed_rules

    def discount_for(self, product_name: str) -> float:
        return self.rules.get(product_name, 0.0)


def test_price_calculator_with_stub():
    rules = PriceRulesStub(
        {"Notebook AVM": 0.15, "AdegaDigital Premium": 0.30})
    calc = PriceCalculator(rules=rules)

    p1 = ProductDTO(id=None, name="Notebook AVM", price=5000.00)
    p2 = ProductDTO(id=None, name="Produto Sem Regra", price=100.00)

    assert math.isclose(calc.final_price(p1), 4250.00, rel_tol=0, abs_tol=1e-9)
    assert math.isclose(calc.final_price(p2), 100.00,  rel_tol=0, abs_tol=1e-9)


class ProductRepoFake(ProductRepo):
    def __init__(self):
        self._store: dict[int, ProductDTO] = {}
        self._seq = 1

    def next_id(self) -> int:
        nid = self._seq
        self._seq += 1
        return nid

    def save(self, product: ProductDTO) -> ProductDTO:
        assert product.id is not None, "ID deve estar definido antes de salvar"
        self._store[product.id] = ProductDTO(**product.__dict__)
        return self._store[product.id]

    def get(self, pid: int) -> ProductDTO | None:
        return self._store.get(pid)


class NotifierSpy(Notifier):
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    def send(self, subject: str, body: str) -> None:
        self.sent.append((subject, body))
    # helper

    def was_called_once_with_subject(self, contains: str) -> bool:
        return len(self.sent) == 1 and contains in self.sent[0][0]


def test_create_product_use_case_with_fake_and_spy():
    repo = ProductRepoFake()
    spy = NotifierSpy()
    usecase = CreateProductUseCase(repo=repo, notifier=spy)

    created = usecase.execute(
        name="SKU-ABC", price=199.90, description="Produto de teste")

    assert created.id == 1
    assert repo.get(1) is not None
    assert repo.get(1).name == "SKU-ABC"
    assert spy.was_called_once_with_subject("Produto #1")
    assert "R$ 199,90" in f"R$ {created.price:.2f}".replace(
        ".", ",")
