---
name: next-best-action
description: Use this skill to rank every open, classified Case by $ Exposure × Urgency into the Servicing Rep's daily Priority Queue, and to re-rank the queue when a case reopens or a supervisor override is applied. Trigger once a Case reaches CLASSIFIED state, or when the whole queue needs recomputing. Reads storyTag/retentionValueUsd/lapseProbability/fitScore already attached by policyholder-insight — this skill does not classify or re-score a story itself, only ranks and assigns.
---

# Next-Best-Action Orchestrator

Turns a pile of classified Cases into one ordered, rep-assigned queue.

## Ranking formula

`priorityScore = retentionValueUsd × lapseProbability × urgencyWeight`

Where `urgencyWeight` defaults to 1.0, but can be configured per segment/geography. Sort descending; the top of the queue is `priority_rank = 1`.

## Tie-break rule

If two Cases have identical `priorityScore`, break the tie by earliest `triggerEvents[0].timestamp` — the older signal is worked first. Ties must resolve deterministically; never leave an arbitrary/random order.

## Assignment

Assign `assignedRepId` using simple round-robin/workload balancing across active reps in this Demo.

## Urgency tiers (for display)

| Tier | Condition |
|---|---|
| P1 – High | `priorityScore` in the top decile of the current open book, or `storyTag = "Flight Risk"` with `lapseProbability > 0.7` |
| P2 – Medium | Everything else with a non-null `recommendedAction` |
| P3 – Low | Classified but `fitScore` below threshold (no pre-filled `recommendedAction`) |

## Output shape (feeds `agent_priority_queue` / the `Case` object)

```json
{
  "taskId": "uuid",
  "caseId": string,
  "policyId": string,
  "assignedRepId": string,
  "priorityRank": number,
  "urgencyLevel": "P1-High" | "P2-Medium" | "P3-Low",
  "recommendedAction": string | null
}
