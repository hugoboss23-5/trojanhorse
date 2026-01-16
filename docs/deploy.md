# Deploy to Render

This repo is deployable to a public HTTPS URL with a single click using
`render.yaml`. The service exposes both the Web UI and API endpoints.

## One-click deploy

1. Push to GitHub (already done).
2. In Render, click **New > Blueprint** and select this repo.
3. Render reads `render.yaml` and provisions:
   - Web service
   - Persistent disk mounted at `/var/data`
   - `FEELD_DB_PATH=/var/data/pipes_api.db`
4. Deploy and wait for the public URL.

## Endpoints (same origin)

- `GET /` (Web UI)
- `GET /health`
- `POST /accounts`
- `POST /transactions`
- `GET /transactions/{id}`
- `GET /ledger/verify`

## Smoke test (curl)

Set the base URL and run:

```
export BASE_URL="https://YOUR-RENDER-URL"
curl -s $BASE_URL/health
curl -s -X POST $BASE_URL/accounts
```

For a full test including signed transactions, use the scripts in
`scripts/`.
