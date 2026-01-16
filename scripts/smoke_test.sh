#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "Health:"
curl -s "$BASE_URL/health"
echo ""

echo "Create account:"
ACCOUNT_JSON=$(curl -s -X POST "$BASE_URL/accounts")
echo "$ACCOUNT_JSON"
ACCOUNT_ID=$(python - <<PY
import json
data=json.loads('''$ACCOUNT_JSON''')
print(data["account_id"])
PY
)
SECRET=$(python - <<PY
import json
data=json.loads('''$ACCOUNT_JSON''')
print(data["secret"])
PY
)

echo "Create recipient account:"
RECIPIENT_JSON=$(curl -s -X POST "$BASE_URL/accounts")
RECIPIENT_ID=$(python - <<PY
import json
data=json.loads('''$RECIPIENT_JSON''')
print(data["account_id"])
PY
)

TX_ID=$(python - <<PY
import json, hmac, hashlib, os, datetime
account_id = "$ACCOUNT_ID"
secret = bytes.fromhex("$SECRET")
to_account = "$RECIPIENT_ID"
payload = {
  "id": "tx" + os.urandom(8).hex(),
  "from_account": account_id,
  "to_account": to_account,
  "amount": "100.00",
  "currency": "USD",
  "created_at": datetime.datetime.utcnow().isoformat() + "Z",
  "metadata": {"purpose": "smoke"},
}
canonical = json.dumps(
  {
    "id": payload["id"],
    "from": payload["from_account"],
    "to": payload["to_account"],
    "amount": payload["amount"],
    "currency": payload["currency"],
    "created_at": payload["created_at"],
    "metadata": payload["metadata"],
  },
  sort_keys=True,
  separators=(",", ":"),
)
sig = hmac.new(secret, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
payload["signature"] = sig
print(payload["id"])
print(json.dumps(payload))
PY
)

TX_ID=$(echo "$TX_ID" | head -n1)
TX_PAYLOAD=$(python - <<PY
import json, hmac, hashlib, os, datetime
account_id = "$ACCOUNT_ID"
secret = bytes.fromhex("$SECRET")
to_account = "$RECIPIENT_ID"
payload = {
  "id": "$TX_ID",
  "from_account": account_id,
  "to_account": to_account,
  "amount": "100.00",
  "currency": "USD",
  "created_at": datetime.datetime.utcnow().isoformat() + "Z",
  "metadata": {"purpose": "smoke"},
}
canonical = json.dumps(
  {
    "id": payload["id"],
    "from": payload["from_account"],
    "to": payload["to_account"],
    "amount": payload["amount"],
    "currency": payload["currency"],
    "created_at": payload["created_at"],
    "metadata": payload["metadata"],
  },
  sort_keys=True,
  separators=(",", ":"),
)
sig = hmac.new(secret, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
payload["signature"] = sig
print(json.dumps(payload))
PY
)

echo "Submit transaction:"
curl -s -X POST "$BASE_URL/transactions" \
  -H "Content-Type: application/json" \
  -d "$TX_PAYLOAD"
echo ""

echo "Lookup receipt:"
curl -s "$BASE_URL/transactions/$TX_ID"
echo ""

echo "Verify ledger:"
curl -s "$BASE_URL/ledger/verify"
echo ""
