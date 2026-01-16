from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .auth import SignedTransaction
from .ledger import Ledger, LedgerEvent
from .models import Receipt, Transaction
from .policies import FeePolicy, SplitPolicy
from .vaults import VaultRegistry


@dataclass(frozen=True)
class RouterConfig:
    fee_rate: Decimal = Decimal("0.01")
    safety_share: Decimal = Decimal("0.5")


class TransactionRouter:
    def __init__(
        self,
        ledger: Ledger,
        vaults: VaultRegistry,
        config: RouterConfig | None = None,
        authorizer=None,
    ) -> None:
        self._ledger = ledger
        self._vaults = vaults
        self._config = config or RouterConfig()
        self._fee_policy = FeePolicy(self._config.fee_rate)
        self._split_policy = SplitPolicy(self._config.safety_share)
        self._authorizer = authorizer

    def route(self, transaction: Transaction | SignedTransaction) -> Receipt:
        if self._authorizer is not None:
            if not isinstance(transaction, SignedTransaction):
                raise ValueError("SignedTransaction required when authorizer set")
            if not self._authorizer.verify(transaction):
                raise ValueError("Transaction signature invalid")
            tx = transaction.transaction
        else:
            tx = transaction if isinstance(transaction, Transaction) else transaction.transaction

        fee = self._fee_policy.compute_fee(tx.amount)
        safety_amount, growth_amount = self._split_policy.split(fee)
        net_amount = tx.amount - fee

        self._ledger.apply(
            LedgerEvent(
                from_account=tx.from_account,
                to_account=tx.to_account,
                amount=net_amount,
                metadata={"transaction_id": tx.id},
            )
        )
        self._ledger.apply(
            LedgerEvent(
                from_account=tx.from_account,
                to_account=self._vaults.safety_vault,
                amount=safety_amount,
                metadata={"transaction_id": tx.id, "vault": "safety"},
            )
        )
        self._ledger.apply(
            LedgerEvent(
                from_account=tx.from_account,
                to_account=self._vaults.growth_vault,
                amount=growth_amount,
                metadata={"transaction_id": tx.id, "vault": "growth"},
            )
        )

        return Receipt(
            transaction_id=tx.id,
            gross_amount=tx.amount,
            net_amount=net_amount,
            fee_amount=fee,
            safety_amount=safety_amount,
            growth_amount=growth_amount,
            vault_safety=self._vaults.safety_vault,
            vault_growth=self._vaults.growth_vault,
            created_at=tx.created_at,
            metadata=tx.metadata or None,
        )
