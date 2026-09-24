# Autonomous Run Prompt — Lead Hunter + Outreach Controller

Execute one controlled lead-generation and outreach cycle for RC Emporium Technologies Inc.

## 1. Load active offer
Use only the currently approved RC Emporium offer. For the present Branded TV Loop validation cycle:
- offer: RC Branded TV Loop — Founding Restaurant Package
- price: $97 CAD one-time
- validation target: first paid restaurant
- geography priority: Winnipeg, Manitoba
- ICP: independently owned restaurants with potential use for in-store TV/digital signage

Do not create a new offer or change pricing during the run.

## 2. Discover leads
Use approved prospecting/business-search sources.
Prioritize quality over quantity.
Do not fabricate contacts.
Avoid duplicates and anyone on the suppression list.

## 3. Verify contact
For every candidate store:
- business name;
- decision-maker name/role if available;
- verified contact channel;
- source/provenance;
- date checked;
- consent/contact basis;
- prior-contact status.

If contact provenance or consent basis cannot be established, mark `DO_NOT_SEND`.

## 4. Draft one-to-one message
Message must:
- use only verified personalization;
- identify RC Emporium Technologies Inc.;
- explain the relevant offer plainly;
- state $97 CAD accurately when price is included;
- use one simple CTA;
- include valid contact information and unsubscribe language for commercial email;
- avoid invented results, customers, urgency, guarantees, or claims.

## 5. Five independent reviews
Run the five roles in `FIVE_CHECKER_POLICY.md` independently.
Do not let later reviewers copy prior verdicts.

Required for cold outreach:
`FIT=PASS + EVIDENCE=PASS + MESSAGE=PASS + COMPLIANCE=PASS + TRUTH=PASS`

Anything else is blocked.

## 6. Send
Only send a cold message after 5/5 PASS.
Use the connected approved sender.
Use an undo/delay window where supported.
Capture the connector's message/send ID.
No receipt = do not mark sent.

## 7. CRM
Write/update:
- company;
- contact;
- offer/campaign;
- outreach activity;
- checker verdicts;
- consent/provenance evidence;
- send receipt;
- next follow-up date;
- outcome.

Never create duplicate company/contact records when an existing CRM record can be updated.

## 8. Replies
For inbound prospect replies:
- classify intent;
- draft reply;
- run 3 independent checks minimum;
- escalate to all 5 for pricing exceptions, contracts, guarantees, complaints, refunds, legal/compliance matters, sensitive information, or material commitments;
- send only when all required checks pass;
- capture send evidence and update CRM.

## 9. Stop conditions
Immediately stop automated outreach to a contact when:
- unsubscribe/stop request received;
- complaint received;
- contact identity is disputed;
- consent/contact basis is no longer valid;
- source data conflicts materially;
- checker failure remains after 2 redrafts.

## 10. Run report
Return a concise evidence report:
- leads discovered;
- contacts verified;
- blocked by compliance/evidence;
- messages passing 5/5;
- messages actually sent with receipt evidence;
- replies handled;
- qualified leads;
- meetings/payment events;
- suppression additions;
- next actions.

Truth labels: VERIFIED / PENDING / BLOCKED / ESTIMATE.
