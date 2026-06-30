# OpenAI Agents

Command/reasoning layer for RC_OS.

## Roles
- Think: strategy, synthesis, engineering review, economic checks
- Verify: claims, math, risks, source consistency
- Generate: specs, prompts, reports, code plans
- Route: decide whether task goes to GitHub, Manus, CIL, or backlog

## Rule
No agent should claim live access to systems unless the connector/tool confirms access during that session.
