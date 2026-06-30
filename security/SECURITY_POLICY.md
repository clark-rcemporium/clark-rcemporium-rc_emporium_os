# Security Policy

## Public Repo Rule
This repository is public. Do not commit raw private vaults, secret-bearing archives, `.env` files, API keys, tokens, passwords, private keys, personal data, or confidential application materials.

## Required Process Before Publishing Vault Data

1. Scan for secrets.
2. Redact sensitive values.
3. Rotate any real credentials found.
4. Commit only sanitized indexes or summaries.
5. Keep raw artifacts in private storage.

## Current Known Risk
Uploaded vault material previously produced redacted possible-secret findings. Treat all raw vault ZIPs as private until reviewed.
