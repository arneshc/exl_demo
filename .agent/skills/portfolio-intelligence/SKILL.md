---

### 10. `.agent/skills/portfolio-intelligence/SKILL.md`

```markdown
---
name: portfolio-intelligence
description: Use this skill to render Stage 1 portfolio-level aggregates for the Chief Actuary / Portfolio Owner dashboard — in-force $, active policy count, retention-opportunity $, lapse-risk exposure $, and product mix, trended over 30D/90D/12M. Trigger for any task about the book-of-business view, the executive dashboard, or a portfolio-level (not single-case) rollup or segment drill-down. Do NOT use this for single-case work (classification, queueing, engagement, proposals) — those are separate skills. This skill only reads; it never writes to a Case.
---

# Portfolio Intelligence

Read-only aggregation layer. Produces the numbers the Portfolio Dashboard screen renders — nothing here mutates a Case or a Policy record.

## Inputs

- Every `<Policyholder>`/`<Policy>` record in `sample_customer_dataset.xml`.
- The `story_tag`, `retention_value_usd`, and `lapse_probability` attached by `policyholder-insight`.

## What to compute

| Metric | Formula |
|---|---|
| In-force $ | Sum of `FaceAmount` across all active policies |
| Active policy count | Count of `<Policy>` nodes |
| Retention opportunity $ | Sum of `retention_value_usd` for policies tagged `Low Lapse / Growth Candidate` |
| Lapse-risk exposure $ | Sum of `retention_value_usd` for policies tagged `Flight Risk` |
| Product mix | % breakdown by `ProductType` |
| Trend (30D/90D/12M) | Plausible trend line labeled **simulated** in output (`simulated: true`) |

## Output shape

```json
{
  "inForceUsd": number,
  "activePolicyCount": number,
  "retentionOpportunityUsd": number,
  "lapseRiskExposureUsd": number,
  "productMix": [{ "productType": string, "pct": number }],
  "trend": { "period": "30D" | "90D" | "12M", "points": [{ "date": string, "value": number }], "simulated": true },
  "segments": [{ "storyTag": string, "policyCount": number, "dollarValue": number, "policyIds": string[] }]
}
