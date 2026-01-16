async function createAccount() {
  const res = await fetch("/accounts", { method: "POST" });
  const data = await res.json();
  document.getElementById("account-output").textContent = JSON.stringify(
    data,
    null,
    2
  );
  if (data.account_id && data.secret) {
    document.getElementById("from-account").value = data.account_id;
    document.getElementById("from-secret").value = data.secret;
  }
}

function hexToBytes(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < bytes.length; i += 1) {
    bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
  }
  return bytes;
}

function canonicalPayload(tx) {
  const payload = {
    id: tx.id,
    from: tx.from_account,
    to: tx.to_account,
    amount: Number(tx.amount).toFixed(2),
    currency: tx.currency,
    created_at: tx.created_at,
    metadata: tx.metadata,
  };
  return JSON.stringify(payload, Object.keys(payload).sort());
}

async function signTransaction(secretHex, tx) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    hexToBytes(secretHex),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign(
    "HMAC",
    key,
    enc.encode(canonicalPayload(tx))
  );
  return Array.from(new Uint8Array(signature))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function sendTransaction() {
  const fromAccount = document.getElementById("from-account").value.trim();
  const fromSecret = document.getElementById("from-secret").value.trim();
  const toAccount = document.getElementById("to-account").value.trim();
  const amount = document.getElementById("amount").value.trim();
  const currency = document.getElementById("currency").value.trim();
  let metadata = {};
  try {
    metadata = JSON.parse(document.getElementById("metadata").value || "{}");
  } catch (err) {
    document.getElementById("tx-output").textContent =
      "Invalid metadata JSON";
    return;
  }
  const tx = {
    id: crypto.randomUUID().replace(/-/g, ""),
    from_account: fromAccount,
    to_account: toAccount,
    amount: amount,
    currency: currency,
    created_at: new Date().toISOString(),
    metadata: metadata,
  };
  const signature = await signTransaction(fromSecret, tx);
  const payload = { ...tx, signature };
  const res = await fetch("/transactions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  document.getElementById("tx-output").textContent = JSON.stringify(
    data,
    null,
    2
  );
  if (data.transaction_id) {
    document.getElementById("lookup-id").value = data.transaction_id;
  }
}

async function lookupReceipt() {
  const txId = document.getElementById("lookup-id").value.trim();
  const res = await fetch(`/transactions/${txId}`);
  const data = await res.json();
  document.getElementById("lookup-output").textContent = JSON.stringify(
    data,
    null,
    2
  );
}

document
  .getElementById("create-account")
  .addEventListener("click", createAccount);
document
  .getElementById("send-transaction")
  .addEventListener("click", sendTransaction);
document
  .getElementById("lookup-transaction")
  .addEventListener("click", lookupReceipt);
