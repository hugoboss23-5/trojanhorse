from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
from typing import Dict, Iterator, List, Optional, Tuple

from .ledger import LedgerEvent
from .models import Money, Receipt


def _to_decimal(value: str) -> Decimal:
    return Decimal(value)


def _serialize_metadata(metadata: Dict[str, str]) -> str:
    return json.dumps(metadata, sort_keys=True, separators=(",", ":"))


def _deserialize_metadata(payload: str) -> Dict[str, str]:
    if not payload:
        return {}
    return json.loads(payload)


def _event_payload(event: LedgerEvent) -> str:
    payload = {
        "id": event.id,
        "created_at": event.created_at.isoformat(),
        "from": event.from_account,
        "to": event.to_account,
        "amount": f"{event.amount.amount:.2f}",
        "currency": event.amount.currency,
        "metadata": event.metadata,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


class SqliteLedger:
    def __init__(self, path: str) -> None:
        self._path = path
        directory = os.path.dirname(os.path.abspath(path))
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS ledger_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    from_account TEXT NOT NULL,
                    to_account TEXT NOT NULL,
                    amount TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    prev_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS balances (
                    account TEXT PRIMARY KEY,
                    balance TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS receipts (
                    transaction_id TEXT PRIMARY KEY,
                    receipt_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id TEXT PRIMARY KEY,
                    secret TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def apply(self, event: LedgerEvent) -> None:
        if event.amount.amount == 0:
            return
        payload = _event_payload(event)
        with self._connect() as conn:
            prev_hash = self._get_last_hash(conn)
            event_hash = self._hash_event(prev_hash, payload)
            conn.execute(
                """
                INSERT INTO ledger_events
                    (event_id, created_at, from_account, to_account, amount,
                     currency, metadata_json, prev_hash, event_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.created_at.isoformat(),
                    event.from_account,
                    event.to_account,
                    f"{event.amount.amount:.2f}",
                    event.amount.currency,
                    _serialize_metadata(event.metadata),
                    prev_hash,
                    event_hash,
                ),
            )
            self._update_balance(conn, event.from_account, -event.amount.amount)
            self._update_balance(conn, event.to_account, event.amount.amount)

    def balance(self, account: str) -> Decimal:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT balance FROM balances WHERE account = ?",
                (account,),
            ).fetchone()
            return _to_decimal(row[0]) if row else Decimal("0")

    def events(self) -> List[LedgerEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT event_id, created_at, from_account, to_account, amount,
                       currency, metadata_json
                FROM ledger_events
                ORDER BY id
                """
            ).fetchall()
            return [self._row_to_event(row) for row in rows]

    def verify_chain(self) -> Tuple[bool, Optional[str]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT prev_hash, event_hash, event_id, created_at, from_account,
                       to_account, amount, currency, metadata_json
                FROM ledger_events
                ORDER BY id
                """
            ).fetchall()
            expected_prev = "GENESIS"
            for row in rows:
                prev_hash, event_hash = row[0], row[1]
                payload = json.dumps(
                    {
                        "id": row[2],
                        "created_at": row[3],
                        "from": row[4],
                        "to": row[5],
                        "amount": row[6],
                        "currency": row[7],
                        "metadata": _deserialize_metadata(row[8]),
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                if prev_hash != expected_prev:
                    return False, "prev_hash mismatch"
                expected_hash = self._hash_event(prev_hash, payload)
                if event_hash != expected_hash:
                    return False, "event_hash mismatch"
                expected_prev = event_hash
        return True, None

    def save_receipt(self, receipt: Receipt) -> None:
        payload = json.dumps(asdict(receipt), default=str, sort_keys=True)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO receipts
                    (transaction_id, receipt_json, created_at)
                VALUES (?, ?, ?)
                """,
                (receipt.transaction_id, payload, receipt.created_at.isoformat()),
            )

    def get_receipt(self, transaction_id: str) -> Optional[Receipt]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT receipt_json FROM receipts WHERE transaction_id = ?",
                (transaction_id,),
            ).fetchone()
            if not row:
                return None
            payload = json.loads(row[0])
            return Receipt(
                transaction_id=payload["transaction_id"],
                gross_amount=Money(_to_decimal(payload["gross_amount"]["amount"]), payload["gross_amount"]["currency"]),
                net_amount=Money(_to_decimal(payload["net_amount"]["amount"]), payload["net_amount"]["currency"]),
                fee_amount=Money(_to_decimal(payload["fee_amount"]["amount"]), payload["fee_amount"]["currency"]),
                safety_amount=Money(_to_decimal(payload["safety_amount"]["amount"]), payload["safety_amount"]["currency"]),
                growth_amount=Money(_to_decimal(payload["growth_amount"]["amount"]), payload["growth_amount"]["currency"]),
                vault_safety=payload["vault_safety"],
                vault_growth=payload["vault_growth"],
                created_at=datetime.fromisoformat(payload["created_at"]),
                metadata=payload.get("metadata"),
            )

    def create_account(self, account_id: str, secret: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO accounts (account_id, secret, created_at)
                VALUES (?, ?, ?)
                """,
                (account_id, secret, datetime.now().isoformat()),
            )

    def get_account_secret(self, account_id: str) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT secret FROM accounts WHERE account_id = ?",
                (account_id,),
            ).fetchone()
            return row[0] if row else None

    @staticmethod
    def _hash_event(prev_hash: str, payload: str) -> str:
        digest = sha256()
        digest.update(prev_hash.encode("utf-8"))
        digest.update(payload.encode("utf-8"))
        return digest.hexdigest()

    @staticmethod
    def _get_last_hash(conn: sqlite3.Connection) -> str:
        row = conn.execute(
            "SELECT event_hash FROM ledger_events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else "GENESIS"

    @staticmethod
    def _row_to_event(row: Tuple[str, str, str, str, str, str, str]) -> LedgerEvent:
        created_at = datetime.fromisoformat(row[1])
        return LedgerEvent(
            from_account=row[2],
            to_account=row[3],
            amount=Money(_to_decimal(row[4]), row[5]),
            id=row[0],
            created_at=created_at,
            metadata=_deserialize_metadata(row[6]),
        )

    @staticmethod
    def _update_balance(
        conn: sqlite3.Connection, account: str, delta: Decimal
    ) -> None:
        row = conn.execute(
            "SELECT balance FROM balances WHERE account = ?",
            (account,),
        ).fetchone()
        if row:
            balance = _to_decimal(row[0]) + delta
            conn.execute(
                "UPDATE balances SET balance = ? WHERE account = ?",
                (f"{balance:.2f}", account),
            )
        else:
            conn.execute(
                "INSERT INTO balances (account, balance) VALUES (?, ?)",
                (account, f"{delta:.2f}"),
            )
