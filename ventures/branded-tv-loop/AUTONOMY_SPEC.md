# Autonomous System Contract

## State machine

1. `PAID`
2. `INTAKE_PENDING`
3. `INTAKE_RECEIVED`
4. `RIGHTS_REVIEW`
5. `RENDERING`
6. `QA`
7. `READY`
8. `DELIVERED`
9. `FOLLOWUP_DUE`
10. `UPSELL_SENT`

Exception states:
- `HUMAN_REVIEW`
- `BLOCKED`
- `FAILED`

## Idempotency

Stripe event IDs are stored and processed once.
Order transitions are append-logged in `order_events`.
Repeated webhook deliveries do not create duplicate orders.

## Autonomy policy

Safe auto-delivery requires all of:
- payment status is paid;
- supplied asset-rights attestation is true;
- audio mode is `silent`;
- venue audio/music is handled separately unless a future rights-reviewed workflow is approved;
- render completes successfully;
- FFprobe checks pass;
- no human-review flag exists;
- `AUTO_DELIVER_SAFE=true`.

Anything else pauses in `HUMAN_REVIEW`.

## Failure behavior

- Never mark a failed render as delivered.
- Never retry indefinitely.
- Render retry maximum: `MAX_RENDER_RETRIES`.
- Preserve error evidence in event log.
- Customer-facing messages must not claim completion before QA PASS.
