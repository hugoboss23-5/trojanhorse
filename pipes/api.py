from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from uuid import uuid4

from .auth import AuthRegistry, HmacAuthorizer, SignedTransaction
from .models import Money, Receipt, Transaction
from .router import TransactionRouter
from .storage import SqliteLedger
from .vaults import VaultRegistry

app = FastAPI(title="FEELD Pipes API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TransactionRequest(BaseModel):
    id: str
    from_account: str = Field(..., min_length=1)
    to_account: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=Decimal("0"))
    currency: str = Field(default="USD", min_length=3, max_length=3)
    created_at: datetime
    metadata: Dict[str, str] = Field(default_factory=dict)
    signature: str


class AccountResponse(BaseModel):
    account_id: str
    secret: str


class ReceiptResponse(BaseModel):
    transaction_id: str
    gross_amount: Dict[str, str]
    net_amount: Dict[str, str]
    fee_amount: Dict[str, str]
    safety_amount: Dict[str, str]
    growth_amount: Dict[str, str]
    vault_safety: str
    vault_growth: str
    created_at: datetime
    metadata: Optional[Dict[str, str]]


def _serialize_money(money: Money) -> Dict[str, str]:
    return {"amount": f"{money.amount:.2f}", "currency": money.currency}


def _serialize_receipt(receipt: Receipt) -> ReceiptResponse:
    return ReceiptResponse(
        transaction_id=receipt.transaction_id,
        gross_amount=_serialize_money(receipt.gross_amount),
        net_amount=_serialize_money(receipt.net_amount),
        fee_amount=_serialize_money(receipt.fee_amount),
        safety_amount=_serialize_money(receipt.safety_amount),
        growth_amount=_serialize_money(receipt.growth_amount),
        vault_safety=receipt.vault_safety,
        vault_growth=receipt.vault_growth,
        created_at=receipt.created_at,
        metadata=receipt.metadata,
    )


def _load_registry() -> AuthRegistry:
    registry = AuthRegistry()
    payload = os.getenv("FEELD_SECRETS", "")
    if payload:
        try:
            secrets_map = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError("FEELD_SECRETS must be valid JSON") from exc
        for account, secret in secrets_map.items():
            registry.register(account, secret)
    return registry


def _build_router() -> tuple[TransactionRouter, SqliteLedger, AuthRegistry]:
    ledger = SqliteLedger(os.getenv("FEELD_DB_PATH", "pipes_api.db"))
    vaults = VaultRegistry(
        safety_vault=os.getenv("FEELD_VAULT_SAFETY", "vault:safety"),
        growth_vault=os.getenv("FEELD_VAULT_GROWTH", "vault:growth"),
    )
    registry = _load_registry()
    if payload := os.getenv("FEELD_DB_ACCOUNTS", ""):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError("FEELD_DB_ACCOUNTS must be valid JSON") from exc
        for account_id, secret in data.items():
            registry.set_secret(account_id, secret)
            ledger.create_account(account_id, secret)
    authorizer = HmacAuthorizer(registry)
    return (
        TransactionRouter(ledger=ledger, vaults=vaults, authorizer=authorizer),
        ledger,
        registry,
    )


router, ledger, registry = _build_router()

WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web")
if os.path.isdir(WEB_DIR):
    app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")


@app.get("/")
def index() -> FileResponse:
    index_path = os.path.join(WEB_DIR, "index.html")
    if not os.path.isfile(index_path):
        raise HTTPException(status_code=404, detail="Web UI not found")
    return FileResponse(index_path)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/transactions", response_model=ReceiptResponse)
def create_transaction(payload: TransactionRequest) -> ReceiptResponse:
    tx = Transaction(
        from_account=payload.from_account,
        to_account=payload.to_account,
        amount=Money(payload.amount, payload.currency),
        id=payload.id,
        created_at=payload.created_at,
        metadata=payload.metadata,
    )
    signed = SignedTransaction(transaction=tx, signature=payload.signature)
    try:
        receipt = router.route(signed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    ledger.save_receipt(receipt)
    return _serialize_receipt(receipt)


@app.get("/transactions/{transaction_id}", response_model=ReceiptResponse)
def get_transaction(transaction_id: str) -> ReceiptResponse:
    receipt = ledger.get_receipt(transaction_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return _serialize_receipt(receipt)


@app.get("/ledger/verify")
def verify_ledger() -> Dict[str, Any]:
    ok, error = ledger.verify_chain()
    return {"ok": ok, "error": error}


@app.post("/accounts", response_model=AccountResponse)
def create_account() -> AccountResponse:
    account_id = f"acct:{uuid4().hex}"
    secret = os.urandom(32).hex()
    ledger.create_account(account_id, secret)
    registry.set_secret(account_id, secret)
    return AccountResponse(account_id=account_id, secret=secret)
