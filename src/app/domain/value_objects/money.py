from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Immutable monetary value object."""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("amount must be >= 0")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("currency must be a 3-letter code")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, factor: float | int | Decimal) -> "Money":
        return Money(self.amount * Decimal(str(factor)), self.currency)
