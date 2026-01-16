from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional
from uuid import uuid4

DEFAULT_CURRENCY = "USD"
DEFAULT_SCALE = Decimal("0.01")


def _quantize(amount: Decimal) -> Decimal:
    return amount.quantize(DEFAULT_SCALE, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = DEFAULT_CURRENCY

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Money.amount must be non-negative")

    def quantized(self) -> "Money":
        return Money(_quantize(self.amount), self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(_quantize(self.amount - other.amount), self.currency)

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(_quantize(self.amount + other.amount), self.currency)

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")


@dataclass(frozen=True)
class Transaction:
    from_account: str
    to_account: str
    amount: Money
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Receipt:
    transaction_id: str
    gross_amount: Money
    net_amount: Money
    fee_amount: Money
    safety_amount: Money
    growth_amount: Money
    vault_safety: str
    vault_growth: str
    created_at: datetime
    metadata: Optional[Dict[str, str]] = None
