"""
FEELD Web Interface
===================

Simple FastAPI backend serving a single-page frontend.
Single FeeldEngine instance persists across all requests.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from feeld_engine import FeeldEngine

app = FastAPI(title="FEELD Payment Engine")

# Single engine instance - persists across requests
engine = FeeldEngine()


class SendRequest(BaseModel):
    amount: int  # in cents


@app.get("/", response_class=HTMLResponse)
async def index():
    return """<!DOCTYPE html>
<html>
<head>
    <title>FEELD Engine</title>
    <meta charset="utf-8">
</head>
<body style="font-family: monospace; max-width: 800px; margin: 40px auto; padding: 20px; background: #111; color: #eee;">

    <h1 style="text-align: center; letter-spacing: 8px; color: #fff;">FEELD</h1>

    <div style="display: flex; gap: 40px; margin: 40px 0;">
        <!-- Safety Vault -->
        <div style="flex: 1; background: #1a1a2e; padding: 30px; text-align: center; border: 2px solid #e94560;">
            <div style="font-size: 12px; color: #e94560; letter-spacing: 4px; margin-bottom: 10px;">LOCKED FOREVER</div>
            <div style="font-size: 14px; color: #888; margin-bottom: 5px;">Safety Vault</div>
            <div id="safety-vault" style="font-size: 48px; font-weight: bold; color: #e94560;">$0.00</div>
        </div>

        <!-- Growth Vault -->
        <div style="flex: 1; background: #1a2e1a; padding: 30px; text-align: center; border: 2px solid #4ae954;">
            <div style="font-size: 12px; color: #4ae954; letter-spacing: 4px; margin-bottom: 10px;">MISSION FUND</div>
            <div style="font-size: 14px; color: #888; margin-bottom: 5px;">Growth Vault</div>
            <div id="growth-vault" style="font-size: 48px; font-weight: bold; color: #4ae954;">$0.00</div>
        </div>
    </div>

    <!-- Send Form -->
    <div style="background: #222; padding: 20px; margin: 20px 0;">
        <div style="display: flex; gap: 10px; align-items: center;">
            <span style="color: #888;">$</span>
            <input type="number" id="amount" step="0.01" min="0.01" placeholder="0.00"
                   style="flex: 1; padding: 15px; font-size: 24px; font-family: monospace; background: #333; border: 1px solid #555; color: #fff;">
            <button onclick="send()"
                    style="padding: 15px 40px; font-size: 18px; font-family: monospace; background: #444; border: 1px solid #666; color: #fff; cursor: pointer;">
                SEND
            </button>
        </div>
        <div style="margin-top: 10px; color: #666; font-size: 12px;">
            1% fee automatically split to vaults (50% each)
        </div>
    </div>

    <!-- Transaction Feed -->
    <div style="margin-top: 40px;">
        <div style="color: #888; font-size: 12px; letter-spacing: 2px; margin-bottom: 10px;">TRANSACTION FEED</div>
        <div id="feed" style="background: #1a1a1a; padding: 10px; min-height: 200px; font-size: 13px; line-height: 1.8;">
            <div style="color: #555;">No transactions yet</div>
        </div>
    </div>

<script>
async function fetchState() {
    const [safetyRes, growthRes, historyRes] = await Promise.all([
        fetch('/api/safety-vault'),
        fetch('/api/growth-vault'),
        fetch('/api/history')
    ]);

    const safety = await safetyRes.json();
    const growth = await growthRes.json();
    const history = await historyRes.json();

    document.getElementById('safety-vault').textContent = formatCents(safety.balance);
    document.getElementById('growth-vault').textContent = formatCents(growth.balance);

    renderFeed(history.transactions);
}

function formatCents(cents) {
    return '$' + (cents / 100).toFixed(2);
}

function renderFeed(transactions) {
    const feed = document.getElementById('feed');
    if (transactions.length === 0) {
        feed.innerHTML = '<div style="color: #555;">No transactions yet</div>';
        return;
    }

    // Show last 10, newest first
    const recent = transactions.slice(-10).reverse();
    feed.innerHTML = recent.map(tx => {
        const time = new Date(tx.timestamp).toLocaleTimeString();
        return `<div style="border-bottom: 1px solid #333; padding: 8px 0;">
            <span style="color: #666;">${time}</span>
            <span style="color: #fff; margin-left: 15px;">${formatCents(tx.amount)}</span>
            <span style="color: #666; margin-left: 10px;">→</span>
            <span style="color: #888; margin-left: 10px;">fee: ${formatCents(tx.fee)}</span>
            <span style="color: #e94560; margin-left: 15px;">+${formatCents(tx.safety_vault_contribution)} safety</span>
            <span style="color: #4ae954; margin-left: 15px;">+${formatCents(tx.growth_vault_contribution)} growth</span>
        </div>`;
    }).join('');
}

async function send() {
    const input = document.getElementById('amount');
    const dollars = parseFloat(input.value);

    if (isNaN(dollars) || dollars <= 0) {
        alert('Enter a valid amount');
        return;
    }

    const cents = Math.round(dollars * 100);

    const res = await fetch('/api/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({amount: cents})
    });

    if (res.ok) {
        input.value = '';
        fetchState();
    } else {
        const err = await res.json();
        alert(err.detail || 'Error');
    }
}

// Handle enter key
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('amount').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') send();
    });
    fetchState();
});
</script>

</body>
</html>"""


@app.get("/api/safety-vault")
async def get_safety_vault():
    return {"balance": engine.get_safety_vault()}


@app.get("/api/growth-vault")
async def get_growth_vault():
    return {"balance": engine.get_growth_vault()}


@app.get("/api/history")
async def get_history():
    return {"transactions": engine.get_transaction_history()}


@app.post("/api/send")
async def send(request: SendRequest):
    try:
        record = engine.send(request.amount)
        return record
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
