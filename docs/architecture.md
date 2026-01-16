# FEELD Pipes: Direct Settlement Architecture

This document describes a payment rail that makes legacy correspondent
banking (SWIFT + nostro/vostro) unnecessary. It is designed for direct
settlement with automatic 1% routing into Safety/Growth vaults.

## Core Idea

Move value on a shared settlement ledger (the "rail") instead of sending
messages between private ledgers. Each participant holds a prefunded
balance on the rail. Transfers are atomic: value moves and fee splits
are recorded in the same transaction.

## Actors

- **Participant**: bank, fintech, or institution using the rail.
- **Validator**: consensus node that orders transactions and produces
  finality. Multiple independent operators.
- **Vaults**: on-ledger accounts for Safety and Growth funding.
- **Issuer** (optional): entity that tokenizes fiat into on-ledger value.

## Ledger Model

Each transaction has:

- Sender account
- Receiver account
- Amount + currency
- 1% fee
- Split: 50% Safety, 50% Growth
- Metadata for compliance/audit

All value movements are recorded on the same ledger, so settlement is
final as soon as the transaction is finalized.

## Transaction Flow

1. **Prefunding**: participants deposit fiat into the system to mint
   on-ledger value (or use existing on-ledger liquidity).
2. **Transfer**: sender signs a transaction.
3. **Validation**: validators verify signatures, balances, and fees.
4. **Atomic Settlement**:
   - Net amount to receiver.
   - Fee to Safety/Growth vaults.
5. **Finality**: transaction is immutable and auditable.

## Fee Routing (Built-In)

Fee = amount * 1%

Split:
- Safety Vault = 50%
- Growth Vault = 50%

Fees are applied and routed in the same atomic transaction to prevent
leakage or disputes.

## Why It’s Simpler Than Correspondent Banking

- No message-only layer; money moves directly on the rail.
- No nostro/vostro accounts; liquidity is on-ledger.
- No multi-hop intermediaries; a single transfer is final.
- Predictable fees and timing.

## Safety Requirements

Minimum requirements for “civilization-safe” operation:

- Multi-operator validator set
- Cryptographic signatures for all transactions
- Tamper-evident ledger with replay protection
- Continuous audit and monitoring
- Disaster recovery and geographic redundancy

## MVP Build Path

1. **Ledger**: persistent, tamper-evident ledger (done in `pipes/storage.py`)
2. **Auth**: signed transactions (done in `pipes/auth.py`)
3. **Router**: atomic fee routing (done in `pipes/router.py`)
4. **API**: HTTP layer for transaction submission and receipts
5. **Validator**: sequencing and finality across multiple nodes
6. **Issuance/Redeem**: fiat on/off ramps

## Next Steps to Implement

- Build the API service (submit transaction, query receipt, verify chain)
- Add multi-node validator prototype (Raft/PBFT or delegated signer set)
- Add account limits, velocity controls, and monitoring

