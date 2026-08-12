---

### 8. `.agent/skills/voice-engagement/SKILL.md`

```markdown
---
name: voice-engagement
description: Use this skill to script and run the Stage 3 in-app AI voice engagement (Gemini Live API, entirely in-browser — no telephony, no human rep on the line) once a Servicing Rep triggers ENGAGEMENT_INITIATED for a case. Pulls the talking points from the matched archetype sub-skill under policyholder-insight, conducts the conversation, tracks sentiment, verifies compliance checkpoints, and identifies the next-best-action from the transcript. Trigger only after a Case already has a storyTag and recommendedAction attached — this skill engages, it does not classify.
---

# Voice Engagement (Call Outreach Agent)

Conducts the actual customer conversation autonomously. No human insurer staff participates live — the human's role is before (triggering) and after (reviewing at `PENDING_REP_APPROVAL`), never during.

## Preconditions

- Case is in `ENGAGEMENT_INITIATED` state with a non-null `storyTag` and `recommendedAction`.
- The matching archetype sub-skill (`flight-risk`, `buyers-remorse`, or `low-lapse-growth`) has already been read for its talking points and disclosure requirements.

## Session flow

1. **Greeting & tenure acknowledgment** — recognize how long the customer has held the policy (`TenureYears`); mark checkpoint verified.
2. **Deliver talking points**, in order specified by sub-skill.
3. **Track sentiment continuously**, recording running `sentimentScore` (-1 to 1).
4. **Verify required disclosures** per matched archetype.
5. **Identify next-best-action at close** — concrete string capturing what was actually agreed.

## Output shape (`VoiceSession`)

```json
{
  "sessionId": string,
  "caseId": string,
  "channel": "IN_APP_VOICE",
  "transcriptRef": string,
  "sentimentScore": number,
  "verifiedCheckpoints": { "greeting": boolean, "tenure_ack": boolean, "disclosure": boolean },
  "nextBestActionIdentified": string | null,
  "initiatedBy": "REP" | "SCHEDULED_RULE",
  "status": "COMPLETED" | "PARTIAL" | "DROPPED"
}
