---

### 3. `.agent/skills/policyholder-insight/SKILL.md`

```markdown
---
name: policyholder-insight
description: Use this skill to tag a single policy with a named story (Flight Risk, Buyer's Remorse, Low Lapse / Growth Candidate, or no active story), plus lapse_probability, retention_value_usd, and fit_score, from PAS + billing/telemetry signals and any available unstructured CRM/call-note context. Trigger whenever a Case reaches or needs to reach CLASSIFIED state, or a portfolio segment needs re-scoring. This skill does NOT contain the scoring logic itself — it matches the policy's signal pattern to one of the archetypes/ sub-skills and defers to that sub-skill for the actual thresholds, dollar-value formula, and recommended action.
---

# Policyholder Insight

Classifier and dispatcher. This skill's only job is to look at a policy's signals and figure out *which* archetype sub-skill applies — then load and run that sub-skill. Never invent scoring logic here; if no sub-skill's trigger condition matches, return the case unclassified rather than guessing.

## Inputs

- `<Policy>` fields: `ProductType`, `FaceAmount`, `CashValue`, `MonthlyPremium`, `IssueDate`, `TenureYears`, `PaymentMode` (and its `riskState`/`note` attributes).
- Associated billing/telemetry signals: `billing_transactions.status`/`failure_reason`, `telemetry_portal_events.event_type` (or, in this Demo, the `<DemoScenarioWiring>` block).
- Optional unstructured context: CRM/service call notes, ingested via Gemini extraction — use as supporting signal only, never as the sole basis for a story tag.

## Dispatch logic

Check sub-skills in this order and stop at the first match — a policy gets exactly one story tag:

1. **`archetypes/flight-risk`** — failed payment + address change + high cash value.
2. **`archetypes/buyers-remorse`** — policy under 90 days old with a delayed first recurring payment.
3. **`archetypes/low-lapse-growth`** — mature, high-cash-value policy on active AutoPay.
4. **No match** → the policy has no active story. Do not force one of the three archetypes onto a policy that doesn't fit; return `storyTag: null`.

Each sub-skill's `SKILL.md` contains its own exact trigger condition, scoring formula, `key_features_json` shape, and the recommended_action/talking points that `voice-engagement` will need later — read the matched sub-skill fully before producing output.

## Output shape (feeds `ml_policy_story_predictions` / the `Case` object)

```json
{
  "policyId": string,
  "storyTag": "Flight Risk" | "Buyer's Remorse" | "Low Lapse / Growth Candidate" | null,
  "lapseProbability": number,
  "retentionValueUsd": number,
  "fitScore": number,
  "keyFeatures": { "...": "boolean flags from the matched archetype" },
  "recommendedAction": string | null
}
