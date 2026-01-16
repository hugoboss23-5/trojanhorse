from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Dict

from .models import Transaction


def normalize_decimal(value: Decimal) -> str:
    return f"{value:.2f}"


def canonical_transaction_payload(tx: Transaction) -> str:
    payload: Dict[str, Any] = {
        "id": tx.id,
        "from": tx.from_account,
        "to": tx.to_account,
        "amount": normalize_decimal(tx.amount.amount),
        "currency": tx.amount.currency,
        "created_at": tx.created_at.isoformat(),
        "metadata": tx.metadata,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
