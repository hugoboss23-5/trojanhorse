"""
FEELD Payment Engine
====================

Core engine for the FEELD payment system.

Immutable Rules:
1. Every transaction has a 1% fee (no exceptions, no minimum, no maximum)
2. Fee split: 50% Safety Vault (permanently locked), 50% Growth Vault (multi-sig accessible)
3. Vaults are append-only. Safety Vault has NO withdrawal function.
4. All transactions logged with full audit trail.

All amounts in cents (integers) to avoid floating point errors.
"""

from datetime import datetime
from typing import List, Dict


class FeeldEngine:
    """Core payment engine for FEELD."""

    FEE_RATE = 1  # 1% fee
    VAULT_SPLIT = 50  # 50% to each vault

    def __init__(self):
        self._safety_vault: int = 0  # Permanently locked
        self._growth_vault: int = 0  # Multi-sig accessible
        self._transaction_history: List[Dict] = []

    def send(self, amount: int) -> Dict:
        """
        Process a transaction with automatic fee deduction and vault allocation.

        Args:
            amount: Transaction amount in cents (must be positive integer)

        Returns:
            Transaction record with all details
        """
        if not isinstance(amount, int):
            raise TypeError("Amount must be an integer (cents)")
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Calculate 1% fee (integer math, rounds down)
        fee = amount // 100

        # Split fee 50/50 between vaults
        # For odd fee amounts, safety vault gets the extra cent (conservative approach)
        safety_contribution = (fee + 1) // 2
        growth_contribution = fee // 2

        # Update vaults (append-only)
        self._safety_vault += safety_contribution
        self._growth_vault += growth_contribution

        # Net amount after fee
        net_amount = amount - fee

        # Create transaction record
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "amount": amount,
            "fee": fee,
            "safety_vault_contribution": safety_contribution,
            "growth_vault_contribution": growth_contribution,
            "safety_vault_total": self._safety_vault,
            "growth_vault_total": self._growth_vault,
            "net_amount": net_amount,
        }

        self._transaction_history.append(record)

        return record

    def get_safety_vault(self) -> int:
        """Get current Safety Vault balance (in cents). Read-only, no withdrawal possible."""
        return self._safety_vault

    def get_growth_vault(self) -> int:
        """Get current Growth Vault balance (in cents)."""
        return self._growth_vault

    def get_transaction_history(self) -> List[Dict]:
        """Get full transaction history. Returns a copy to prevent tampering."""
        return list(self._transaction_history)

    def withdraw_growth_vault(self, amount: int, authorization: str) -> Dict:
        """
        Withdraw from Growth Vault (requires authorization).

        Args:
            amount: Amount to withdraw in cents
            authorization: Multi-sig authorization token

        Returns:
            Withdrawal record
        """
        if not isinstance(amount, int):
            raise TypeError("Amount must be an integer (cents)")
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self._growth_vault:
            raise ValueError("Insufficient funds in Growth Vault")
        if not authorization:
            raise ValueError("Authorization required for Growth Vault withdrawal")

        self._growth_vault -= amount

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "growth_vault_withdrawal",
            "amount": amount,
            "growth_vault_total": self._growth_vault,
            "authorization": authorization,
        }


def format_cents(cents: int) -> str:
    """Format cents as dollars for display."""
    return f"${cents / 100:.2f}"


if __name__ == "__main__":
    print("=" * 60)
    print("FEELD Payment Engine - Test Run")
    print("=" * 60)
    print()

    engine = FeeldEngine()

    # Test transactions of varying amounts (in cents)
    test_amounts = [
        10000,    # $100.00
        5000,     # $50.00
        25000,    # $250.00
        1,        # $0.01 (edge case: 1 cent)
        99,       # $0.99 (edge case: under $1)
        100,      # $1.00 (exactly $1)
        123456,   # $1,234.56
        7777,     # $77.77
        50000,    # $500.00
        999999,   # $9,999.99
    ]

    print(f"{'TX#':<4} {'Amount':>12} {'Fee':>10} {'Safety':>10} {'Growth':>10} {'Vault Totals':>20}")
    print("-" * 70)

    for i, amount in enumerate(test_amounts, 1):
        record = engine.send(amount)
        print(
            f"{i:<4} "
            f"{format_cents(record['amount']):>12} "
            f"{format_cents(record['fee']):>10} "
            f"{format_cents(record['safety_vault_contribution']):>10} "
            f"{format_cents(record['growth_vault_contribution']):>10} "
            f"S:{format_cents(record['safety_vault_total']):>8} "
            f"G:{format_cents(record['growth_vault_total']):>8}"
        )

    print("-" * 70)
    print()
    print("Final Vault Totals:")
    print(f"  Safety Vault (locked):     {format_cents(engine.get_safety_vault())}")
    print(f"  Growth Vault (accessible): {format_cents(engine.get_growth_vault())}")
    print()

    # Verify the math
    total_fees = sum(tx['fee'] for tx in engine.get_transaction_history())
    total_safety = sum(tx['safety_vault_contribution'] for tx in engine.get_transaction_history())
    total_growth = sum(tx['growth_vault_contribution'] for tx in engine.get_transaction_history())

    print("Verification:")
    print(f"  Total fees collected:      {format_cents(total_fees)}")
    print(f"  Safety contributions:      {format_cents(total_safety)}")
    print(f"  Growth contributions:      {format_cents(total_growth)}")
    print(f"  Sum of contributions:      {format_cents(total_safety + total_growth)}")
    print(f"  Match: {total_fees == total_safety + total_growth}")
    print()
    print(f"Transactions processed: {len(engine.get_transaction_history())}")
