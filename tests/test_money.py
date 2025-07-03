from decimal import Decimal

import pytest

from app.domain.value_objects.money import Money


def test_negative_amount_raises() -> None:
    with pytest.raises(ValueError):
        Money(Decimal("-1"), "USD")


def test_invalid_currency() -> None:
    with pytest.raises(ValueError):
        Money(Decimal("1"), "US")


def test_add_preserves_immutability() -> None:
    m1 = Money(Decimal("10"), "USD")
    m2 = Money(Decimal("5"), "USD")
    result = m1 + m2
    assert result.amount == Decimal("15")
    assert m1.amount == Decimal("10")
