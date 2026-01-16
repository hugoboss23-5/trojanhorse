from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .models import Money, _quantize


@dataclass(frozen=True)
class FeePolicy:
    fee_rate: Decimal

    def compute_fee(self, amount: Money) -> Money:
        if self.fee_rate < 0:
            raise ValueError("fee_rate must be non-negative")
        fee = _quantize(amount.amount * self.fee_rate)
        return Money(fee, amount.currency)


@dataclass(frozen=True)
class SplitPolicy:
    safety_share: Decimal

    def split(self, fee: Money) -> tuple[Money, Money]:
        if not (Decimal("0") <= self.safety_share <= Decimal("1")):
            raise ValueError("safety_share must be between 0 and 1")
        safety_amount = _quantize(fee.amount * self.safety_share)
        growth_amount = _quantize(fee.amount - safety_amount)
        return (
            Money(safety_amount, fee.currency),
            Money(growth_amount, fee.currency),
        )
