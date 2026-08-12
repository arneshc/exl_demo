---
name: buyers-remorse
description: Sub-skill of policyholder-insight. Use when a policy is under 90 days old and its first recurring payment was delayed — the early-tenure hesitation pattern (e.g. Ashley Thompson, David Nguyen in the sample dataset). Contains the trigger condition, scoring approach, and the reassurance-oriented recommended action and talking points for voice-engagement. Do not use once a policy is past its first-90-day window even if other risk signals are present — that belongs to a different archetype.
---

# Archetype: Buyer's Remorse

## Trigger condition (all must hold)

- `TenureYears` < 0.25 (i.e., issued within roughly the last 90 days).
- `PaymentMode` carries a note indicating the first recurring payment was delayed (in this Demo: the `note="First recurring payment delayed"` attribute on `<PaymentMode>`).
- `riskState="true"` on `PaymentMode`.

## Scoring

- `lapseProbability`: moderate-high (0.5–0.7 range) — early hesitation is a real lapse signal but less acute than a confirmed Flight Risk double-signal.
- `retentionValueUsd` = `FaceAmount`, but note this is a *new* policy — the insurer's actual sunk cost/commission exposure is different from a mature policy's; flag this distinction if the consuming skill needs it for prioritization.
- `fitScore`: moderate (0.4–0.6) — early-tenure customers are harder to predict than an established relationship.
- `keyFeatures`: `{ "new_policy": true, "delayed_first_payment": true }`.

## Recommended action & talking points

- `recommendedAction`: `"Reassurance Check-In"` — explicitly **not** a rider or upsell offer; the goal is confidence, not more commitment.
- Talking points, in order:
  1. Open warmly, low-pressure — this is a welcome/check-in, not a collections call.
  2. Ask directly and non-judgmentally whether anything about the policy is unclear or has changed since purchase.
  3. Reiterate the core benefit in plain language (what the policy actually protects, in the customer's own terms if known).
  4. Offer to fix the payment method on the spot if the delay was a logistics issue, without dwelling on the missed payment itself.
- Do **not** offer additional riders or face-amount increases at this stage — a customer this early who's shown hesitation is not a cross-sell opportunity yet.

## Output feeding into `Case`

`storyTag: "Buyer's Remorse"`, plus the fields above assembled into the shape defined in the parent `policyholder-insight/SKILL.md`.
