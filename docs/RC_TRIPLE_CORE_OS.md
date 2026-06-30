# RC Triple-Core OS

## Architecture

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

## Execution Loop

```text
THINK → OpenAI
STORE → GitHub
BUILD → Manus
VERIFY → ChatGPT/OpenAI
ARCHIVE → GitHub + Vault
```

## Tool Roles

| Layer | Tool | Role |
|---|---|---|
| Brain | ChatGPT / OpenAI Platform | strategy, specs, reasoning, verification |
| Source of truth | GitHub | code, manifests, decisions, backlog, issues |
| Builder | Manus | sites, apps, decks, research, dashboards |
| Archive | Vault + CIL | raw evidence + structured memory |

## Non-Negotiables

- No fake data.
- No fake customers or revenue.
- No unverified technical performance claims.
- No raw secret uploads to public repos.
- Manus outputs must be verified before being treated as completed.
- RCBID remains revenue-first priority.
- VEPKAR remains frozen except for safe IP strategy/documentation work.
