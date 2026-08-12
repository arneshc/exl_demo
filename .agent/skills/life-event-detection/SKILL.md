---
name: life-event-detection
description: Use this skill to watch telemetry/billing signals (telemetry_portal_events, billing_transactions — or the <DemoScenarioWiring> block in this Demo) and open a new Case automatically when a meaningful event lands (address change, payment failure, beneficiary change). Trigger this when a policy has a new event and no open Case yet, or when an event lands against an existing open Case (run the dedupe check). This skill only detects and opens/dedupes Cases — it does NOT classify a story (that's policyholder-insight) or rank a queue (that's next-best-action).
---

# Life-Event Detection

The entry point of the pipeline. Produces a `Case` in `DETECTED` state and nothing more.

## Inputs

- `telemetry_portal_events`: `event_type` (e.g. `ADDRESS_UPDATE`, `BENEFICIARY_UPDATE`), `old_value_json`, `new_value_json`, `timestamp`.
- `billing_transactions`: `status`, `failure_reason`, `attempt_date`.
- In this Demo, both are represented by the `<DemoScenarioWiring>` block's `<TelemetryEvent>` and `<BillingTransaction>` nodes.

## What counts as a triggering event

Any single event is enough to open a Case; classification of *how meaningful* it is happens downstream in `policyholder-insight`. This skill's job is completeness, not judgment — don't filter out an event because it looks minor.

## Dedupe rule

Before opening a new Case, check for an existing open Case (`status` not in `CLOSED`/`ESCALATED`) on the same `policyId`. If one exists and a new event lands within a short window (recommend: 24–48h, configurable), attach the new event to the existing Case rather than opening a second one. Two address-change events in quick succession are one Case, not two.

## Output shape

```json
{
  "caseId": "uuid",
  "policyId": string,
  "holderId": string,
  "status": "DETECTED",
  "triggerEvents": [{ "type": string, "oldValue": object, "newValue": object, "timestamp": string }],
  "createdAt": string
}
