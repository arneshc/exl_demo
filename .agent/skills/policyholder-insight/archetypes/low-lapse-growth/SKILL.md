---
name: low-lapse-growth
description: Sub-skill of policyholder-insight. Use when a policy is mature, high-cash-value, and on active AutoPay/Direct Debit — a low-risk, high-upside cross-sell candidate (e.g. Robert Johnson, Linda Park in the sample dataset). Contains the trigger condition and the growth-oriented recommended action and talking points for voice-engagement. This is the one archetype where the goal is upsell, not retention — do not apply retention-style urgency framing here.
---

# Archetype: Low Lapse / Growth Candidate

## Trigger condition (all must hold)

- `TenureYears` > 10 (mature policy).
- `CashValue` is a large fraction of `FaceAmount` (meaningful accumulated cash value — e.g. Robert Johnson: $98,750 cash value on $150,000 face; Linda Park: $187,500 on $300,000 face).
- `PaymentMode` = AutoPay/Direct Debit with `riskState="false"` (no payment friction at all — this is a stable relationship, not a risk case).

## Scoring

- `lapseProbability`: low (0.05–0.15) — this archetype is explicitly *not* a lapse risk; don't inflate this number to make the case seem more urgent than it is.
- `retentionValueUsd`: use `CashValue` (the growth/upsell opportunity), not `FaceAmount` — this number represents *potential*, not *at-risk* dollars, and downstream consumers (e.g. the Portfolio Dashboard's "Retention Opportunity $" aggregate) expect it framed that way.
- `fitScore`: high (0.7–0.9) — a stable, high-cash-value, no-friction relationship is a strong conversion candidate for a low-pressure offer.
- `keyFeatures`: `{ "mature_policy": true, "high_cash_value_ratio": true, "stable_autopay": true }`.

## Recommended action & talking points

- `recommendedAction`: `"Cross-Sell / Growth Conversation"` (e.g. paid-up additions, a policy loan option, or a rider upgrade funded by cash value).
- Talking points, in order:
  1. Lead with appreciation for tenure — this is a long-standing, well-managed relationship; the tone is celebratory, not corrective.
  2. Surface the cash-value growth as a concrete number the customer may not realize they have.
  3. Introduce one relevant growth option (not a menu of five) matched to `DependentsCount`/apparent life stage if known from CRM context.
  4. No urgency language — there is no lapse risk to create pressure around; let the customer set the pace.

## Output feeding into `Case`

`storyTag: "Low Lapse / Growth Candidate"`, plus the fields above assembled into the shape defined in the parent `policyholder-insight/SKILL.md`.
