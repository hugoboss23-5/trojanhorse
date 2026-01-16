# Contracts

Prototype Solidity contracts for the FEELD rail. These are not audited.
For production, use OpenZeppelin ERC-20 and a formal audit process.

## `FeeldToken.sol`

ERC-20 style token with a fixed 1% fee on every transfer:

- 0.5% to Safety Vault
- 0.5% to Growth Vault

The fee is enforced in `_transfer()`, so it cannot be bypassed.

## Notes

- This contract is a starting point, not production-ready.
- Use Arbitrum for deployment per your requirement.
- We can add account-abstraction wallets and relayers later for
  “sign up once” UX without custody.
