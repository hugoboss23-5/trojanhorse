# trojanhorse

Core "pipes" for FEELD-style routing are in `pipes/`. This is a hardened
prototype that applies a fee, splits it into safety/growth vaults, and
records all movements with a tamper-evident hash chain and signed
transactions.

Quick start:

```
python -m pipes.demo
```

This uses a SQLite-backed ledger (`pipes_demo.db`), HMAC signing, and a
hash-chained audit log. It is still a prototype and not production
infrastructure; it is the foundation for the next build phase.

Architecture and MVP plan:
- `docs/architecture.md`
- `docs/mvp.md`

API quick start (PowerShell):

```
$env:FEELD_SECRETS='{"acct:alice":"<hex-secret>"}'
python -m uvicorn pipes.api:app --reload
```

Create accounts once via `POST /accounts` (returns account id + secret),
then use those credentials forever to sign transactions. Query receipts
by id.

Web UI:
- Start the API and open `http://127.0.0.1:8000/` in a browser.

Solidity prototype:
- `contracts/FeeldToken.sol`
- `contracts/README.md`