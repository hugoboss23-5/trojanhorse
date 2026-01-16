from __future__ import annotations

import hmac
import secrets
from dataclasses import dataclass
from hashlib import sha256
from typing import Dict, Optional

from .models import Transaction
from .serialization import canonical_transaction_payload


@dataclass(frozen=True)
class SignedTransaction:
    transaction: Transaction
    signature: str
    key_id: Optional[str] = None


class AuthRegistry:
    def __init__(self) -> None:
        self._secrets: Dict[str, str] = {}

    def register(self, account: str, secret: Optional[str] = None) -> str:
        generated = secret or secrets.token_hex(32)
        self._secrets[account] = generated
        return generated

    def get_secret(self, account: str) -> Optional[str]:
        return self._secrets.get(account)

    def set_secret(self, account: str, secret: str) -> None:
        self._secrets[account] = secret


class HmacAuthorizer:
    def __init__(self, registry: AuthRegistry) -> None:
        self._registry = registry

    def sign(self, transaction: Transaction) -> SignedTransaction:
        secret = self._registry.get_secret(transaction.from_account)
        if not secret:
            raise ValueError("No secret registered for from_account")
        signature = self._compute_signature(secret, transaction)
        return SignedTransaction(transaction=transaction, signature=signature)

    def verify(self, signed_tx: SignedTransaction) -> bool:
        secret = self._registry.get_secret(signed_tx.transaction.from_account)
        if not secret:
            return False
        expected = self._compute_signature(secret, signed_tx.transaction)
        return hmac.compare_digest(expected, signed_tx.signature)

    @staticmethod
    def _compute_signature(secret: str, tx: Transaction) -> str:
        payload = canonical_transaction_payload(tx).encode("utf-8")
        return hmac.new(secret.encode("utf-8"), payload, sha256).hexdigest()
