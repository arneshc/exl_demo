---

### 4. `.agent/skills/policyholder-insight/archetypes/flight-risk/SKILL.md`

```markdown
---
name: flight-risk
description: Sub-skill of policyholder-insight. Use when a policy shows a failed payment combined with a recent address change and meaningful cash value — the flagship demo signal pattern (Michael Carter / Michael Turner). Contains the exact trigger condition, scoring formula, dollar-exposure calculation, and the recommended action and talking points the voice-engagement skill should use if this archetype is selected. Do not use for a policy without a failed-payment signal in the current window.
---

# Archetype: Flight Risk

## Trigger condition (all must hold)

- A `billing_transactions` record with `status = FAILED` in the current window (in this Demo: the `<BillingTransaction>` under `<DemoScenarioWiring>`).
- A `telemetry_portal_events` record with `event_type = ADDRESS_UPDATE` within the same recent window (in this Demo: the `<TelemetryEvent>` under `<DemoScenarioWiring>`).
- `CashValue` is materially above zero (i.e., not a brand-new term policy with no cash value) — this is what makes the exposure worth acting on.

## Scoring

- `lapseProbability`: use the demo-provided value where available (`LapseProbability30Day`, e.g. 0.84); otherwise default to **0.75–0.90** for a confirmed double-signal match, scaled down toward 0.5 if only one of the two signals is present (and in that case, do not tag Flight Risk at all — the dispatch rule requires both).
- `retentionValueUsd` = the policy's `FaceAmount` (the amount actually at risk if the policy lapses).
- `fitScore`: use the demo-provided value where available (`FitScore`, e.g. 0.96); otherwise estimate from signal strength (both signals + high cash value → 0.9+).
- `keyFeatures`: `{ "failed_payment": true, "address_change": true, "high_cash_value": true }`.

## Recommended action & talking points (for `voice-engagement`)

- `recommendedAction`: `"Retention / AutoPay Setup + [applicable rider]"` (e.g. Child Education Rider if `DependentsCount > 0`).
- Talking points, in order:
  1. Acknowledge the tenure (`TenureYears`) and the life event (address change) warmly, not transactionally.
  2. Name the payment friction directly and normalize it (bank/card transitions are common after a move).
  3. Offer AutoPay / Direct Debit as the fix, framed around protecting the accumulated cash value.
  4. If `DependentsCount > 0`, soft-offer a relevant rider (e.g. Child Education Benefit) tied to the family context — do not force this if the customer is not receptive.
- Required disclosure: standard payment-authorization disclosure before switching payment mode; do not let `proposal-generation` finalize the AutoPay change without it.

## Output feeding into `Case`

`storyTag: "Flight Risk"`, plus the fields above assembled into the shape defined in the parent `policyholder-insight/SKILL.md`.
