from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List
from uuid import uuid4

from .models import Money


@dataclass(frozen=True)
class LedgerEvent:
    from_account: str
    to_account: str
    amount: Money
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: Dict[str, str] = field(default_factory=dict)


class Ledger:
    def __init__(self) -> None:
        self._events: List[LedgerEvent] = []
        self._balances: Dict[str, Decimal] = {}

    def apply(self, event: LedgerEvent) -> None:
        if event.amount.amount == 0:
            return
        self._events.append(event)
        self._balances[event.from_account] = (
            self._balances.get(event.from_account, Decimal("0"))
            - event.amount.amount
        )
        self._balances[event.to_account] = (
            self._balances.get(event.to_account, Decimal("0"))
            + event.amount.amount
        )

    def balance(self, account: str) -> Decimal:
        return self._balances.get(account, Decimal("0"))

    def events(self) -> List[LedgerEvent]:
        return list(self._events)
