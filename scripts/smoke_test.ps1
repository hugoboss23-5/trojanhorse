$ErrorActionPreference = "Stop"

$BaseUrl = $env:BASE_URL
if (-not $BaseUrl) {
  $BaseUrl = "http://127.0.0.1:8000"
}

Write-Host "Health:"
Invoke-RestMethod "$BaseUrl/health" | ConvertTo-Json -Depth 5

Write-Host "Create account:"
$account = Invoke-RestMethod -Method Post "$BaseUrl/accounts"
$account | ConvertTo-Json -Depth 5

Write-Host "Create recipient account:"
$recipient = Invoke-RestMethod -Method Post "$BaseUrl/accounts"

$txId = "tx" + ([Guid]::NewGuid().ToString("N"))
$payload = @{
  id = $txId
  from_account = $account.account_id
  to_account = $recipient.account_id
  amount = "100.00"
  currency = "USD"
  created_at = (Get-Date).ToUniversalTime().ToString("o")
  metadata = @{ purpose = "smoke" }
}

$metaOrdered = [ordered]@{}
$payload.metadata.Keys | Sort-Object | ForEach-Object { $metaOrdered[$_] = $payload.metadata[$_] }

$canonical = [ordered]@{
  amount = $payload.amount
  created_at = $payload.created_at
  currency = $payload.currency
  from = $payload.from_account
  id = $payload.id
  metadata = $metaOrdered
  to = $payload.to_account
} | ConvertTo-Json -Compress

$secretBytes = for ($i = 0; $i -lt $account.secret.Length; $i += 2) {
  [Convert]::ToByte($account.secret.Substring($i, 2), 16)
}

$hmac = New-Object System.Security.Cryptography.HMACSHA256
$hmac.Key = $secretBytes
$signatureBytes = $hmac.ComputeHash([Text.Encoding]::UTF8.GetBytes($canonical))
$signature = ($signatureBytes | ForEach-Object { $_.ToString("x2") }) -join ""

$payload.signature = $signature

Write-Host "Submit transaction:"
Invoke-RestMethod -Method Post "$BaseUrl/transactions" -Body ($payload | ConvertTo-Json -Depth 5) -ContentType "application/json" |
  ConvertTo-Json -Depth 5

Write-Host "Lookup receipt:"
Invoke-RestMethod "$BaseUrl/transactions/$txId" | ConvertTo-Json -Depth 5

Write-Host "Verify ledger:"
Invoke-RestMethod "$BaseUrl/ledger/verify" | ConvertTo-Json -Depth 5
