# RC Lead Hunter + 5-Checker Outreach Controller

Company: RC Emporium Technologies Inc.
Status: PROPOSED — NOT CANONICAL

## Purpose

One controlled agent system for lead discovery, contact verification, compliant outreach, reply handling, follow-ups, CRM updates, and evidence logging.

This consolidates prior RC Emporium lead/outreach concepts rather than creating another incompatible CRM.

## Connected operating stack

- Lead discovery / enrichment: AI Vibe Prospecting or verified public business sources.
- CRM system of record: existing `sales-analytics-crm` repository/data model.
- Email drafting and sending: Superhuman Mail connected account.
- Strategy / orchestration / review: ARCEE / ChatGPT.
- Evidence / configuration: RC Emporium OS / GitHub.

## Core pipeline

DISCOVERED
→ ENRICHING
→ CONTACT_VERIFIED
→ CONSENT_BASIS_VERIFIED
→ DRAFTED
→ REVIEW_1
→ REVIEW_2
→ REVIEW_3
→ REVIEW_4
→ REVIEW_5
→ APPROVED_TO_SEND
→ SENT_VERIFIED
→ REPLIED
→ RESPONSE_DRAFTED
→ RESPONSE_REVIEWED
→ FOLLOW_UP
→ QUALIFIED
→ WON / LOST / DO_NOT_CONTACT

## Send rule

### First-touch / cold outreach

**5/5 reviewers must PASS.**

Any FAIL or UNKNOWN blocks sending.

### Routine replies / follow-ups

Minimum **3/3 reviewers must PASS**.

Escalate back to all 5 whenever a reply includes pricing changes, legal/compliance questions, contracts, claims about results, refunds, guarantees, sensitive customer information, or another material risk.

## 5 Checker roles

1. **Lead Fit Checker** — verifies company/person fit, role relevance, duplicate status, and reason to contact.
2. **Evidence Checker** — verifies contact identity/address/source and rejects guessed or fabricated details.
3. **Message Checker** — verifies personalization, clarity, offer accuracy, tone, and no hallucinated facts.
4. **Compliance Checker** — verifies documented consent basis, sender identification, contact information, unsubscribe language, suppression list, and jurisdiction rules.
5. **Truth + Reputation Checker** — verifies no false claims, fake urgency, fake customers, fake scarcity, misleading pricing, or reputationally risky wording.

## Approval logic

```text
FIRST TOUCH:
IF C1=PASS AND C2=PASS AND C3=PASS AND C4=PASS AND C5=PASS
  → APPROVED_TO_SEND
ELSE
  → BLOCKED_REVIEW

ROUTINE REPLY:
IF R1=PASS AND R2=PASS AND R3=PASS AND risk_level=LOW
  → APPROVED_TO_SEND
ELSE
  → RUN_ALL_5
```

## Compliance lock

For Canadian commercial electronic messages, the system must store a `consent_basis` before sending. Permitted categories must be evidence-backed, for example:

- express consent;
- existing business relationship within the applicable period;
- inquiry/request that permits a relevant response;
- conspicuously published business contact information where there is no statement against unsolicited commercial messages and the message is relevant to the recipient's business role.

No documented basis = **DO NOT SEND**.

Every outbound commercial email must contain:

- RC Emporium Technologies Inc. identification;
- valid contact method;
- truthful offer/pricing language;
- simple unsubscribe instruction;
- suppression check before send.

Unsubscribe requests move the contact immediately to `DO_NOT_CONTACT` and must not be re-added by later enrichment.

## Contact verification

Never send to an address merely inferred from a naming pattern.

Accepted evidence examples:

- enriched contact record from an approved lead-data connector;
- contact details on the recipient/company's verified site;
- prior inbound correspondence;
- authenticated CRM record with provenance.

Store source URL/provider, checked timestamp, confidence, and verifier result.

## Duplicate protection

Before sending, match on:

- normalized email;
- company domain + full name;
- company + role;
- prior CRM activity;
- suppression/unsubscribe history.

Duplicate or previously contacted leads are routed to follow-up logic, not treated as new cold leads.

## Evidence requirements

A message may be marked `SENT_VERIFIED` only after the sending connector returns a send receipt/message ID. Draft creation is not evidence of sending.

Record for every outbound item:

- lead/contact ID;
- campaign/offer;
- source/provenance;
- consent basis and evidence;
- message version;
- five checker results;
- final approval timestamp;
- send connector receipt/message ID;
- follow-up due date;
- reply/outcome.

## Initial commercial use

For RC Branded TV Loop, prioritize independently owned Winnipeg restaurants with visible in-store TVs/digital signage potential and a reachable owner/manager or marketing/operations decision-maker.

Offer currently tested: **$97 CAD founding restaurant package**.

Do not invent customer results, conversion claims, or social proof.
