# RC Emporium OS

**Purpose:** unified operating layer for RC Emporium Technologies Inc.

This repository is the source-of-truth control layer for the RC_OS architecture:

```text
User / Clark
   ↓
ChatGPT / OpenAI Platform
   ↓
RC_OS Command Layer
   ↓
GitHub Repo: rc-os / rcbid / cil / vault
   ↓
Manus Builder Tasks
   ↓
Outputs: websites, apps, reports, dashboards
   ↓
Back into GitHub + CIL Vault
```

## Operating Rule

```text
THINK → OpenAI
STORE → GitHub
BUILD → Manus
VERIFY → ChatGPT/OpenAI
ARCHIVE → GitHub + Vault
```

## Source-of-Truth Policy

- GitHub stores the repo structure, manifests, specs, task logs, and non-secret indexes.
- The RC_MANUS_DATA_VAULT ZIP remains private unless secrets are reviewed/redacted.
- CIL stores structured venture/IP/skill/task records.
- Manus is treated as a builder/executor, not the master storage layer.
- OpenAI/ChatGPT is the command, reasoning, verification, and synthesis layer.

## Phase Gate

Current gate: **Scope → Design Freeze**

Next gate: **Source** — import safe manifests, then push sanitized CIL records.
