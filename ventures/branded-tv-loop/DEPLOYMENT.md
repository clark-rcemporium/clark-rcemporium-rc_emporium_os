# Deployment Sequence

## Gate 0 — current state

Commercial validation is still pending. Do not spend heavily on infrastructure.

## Gate 1 — first paid restaurant

After the first real payment:

1. Deploy this container to a host with persistent storage.
2. Mount persistent storage at `/data`.
3. Set HTTPS `APP_BASE_URL`.
4. Add Stripe secret key and webhook signing secret as host secrets.
5. Point Stripe `checkout.session.completed` webhook to `/webhooks/stripe`.
6. Configure transactional email.
7. Set founder email.
8. Keep `AUTO_DELIVER_SAFE=true` only for silent/original-audio orders.
9. Test with one controlled live purchase.
10. Verify exactly-once order creation, intake, render, QA, delivery, and idempotency.

## Gate 2 — recurring managed-update service

Only after customers actually use the loops:
- add recurring subscription;
- add content scheduling;
- add multi-screen variants;
- add customer self-service updates.

## Security

Never commit Stripe secret keys, webhook signing secrets, email keys, admin tokens, or customer private assets.
