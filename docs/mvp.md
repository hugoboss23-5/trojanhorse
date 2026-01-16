# MVP: Direct Settlement Rail

This MVP proves that money can move directly between participants without
correspondent banking, while enforcing the 1% Safety/Growth fee split.

## MVP Goals

- Direct transfer between accounts with immediate finality
- Automatic 1% fee routing
- Tamper-evident audit trail
- Signed transaction authorization
- Simple API for integration

## Components

- **Ledger**: SQLite-backed hash-chained event log
- **Router**: applies fee and writes all movements atomically
- **Auth**: HMAC signatures for transaction authorization
- **API** (next): HTTP service for submit/query

## Immediate Build Tasks

1. Add API server:
   - `POST /transactions` (submit signed transaction)
   - `GET /transactions/{id}` (receipt)
   - `GET /ledger/verify` (audit verification)
2. Add receipt storage for lookup by transaction ID.
3. Add basic monitoring: counts, volumes, vault balances.

## Target Outcomes

- One-transaction finality
- Predictable fee routing
- Publicly verifiable ledger integrity

