# Vault

Private artifact storage index for RC_MANUS_DATA_VAULT packages.

## Rule
Do not commit raw ZIP vaults, `.env` files, API keys, access tokens, or private customer/grant materials into this public repo.

Store only:
- sanitized manifests
- hash indexes
- redacted security reports
- file-location references
- import instructions

Current local vault baseline: `RC_MANUS_DATA_VAULT_V5.zip`.

Status: **private / not committed** until security review is complete.
