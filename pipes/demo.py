from decimal import Decimal

from pipes import (
    AuthRegistry,
    HmacAuthorizer,
    Money,
    SqliteLedger,
    Transaction,
    TransactionRouter,
    VaultRegistry,
 )


def run() -> None:
    ledger = SqliteLedger("pipes_demo.db")
    vaults = VaultRegistry(safety_vault="vault:safety", growth_vault="vault:growth")
    auth_registry = AuthRegistry()
    auth_registry.register("acct:alice")
    authorizer = HmacAuthorizer(auth_registry)
    router = TransactionRouter(ledger=ledger, vaults=vaults, authorizer=authorizer)

    tx = Transaction(
        from_account="acct:alice",
        to_account="acct:merchant",
        amount=Money(Decimal("100.00"), "USD"),
        metadata={"purpose": "groceries"},
    )

    signed_tx = authorizer.sign(tx)
    receipt = router.route(signed_tx)
    print("receipt:", receipt)
    print(
        "balances:",
        {
            "acct:alice": str(ledger.balance("acct:alice")),
            "acct:merchant": str(ledger.balance("acct:merchant")),
            "vault:safety": str(ledger.balance("vault:safety")),
            "vault:growth": str(ledger.balance("vault:growth")),
        },
    )
    print("chain verification:", ledger.verify_chain())


if __name__ == "__main__":
    run()
