---

### 9. `.agent/skills/proposal-generation/SKILL.md`

```markdown
---
name: proposal-generation
description: Use this skill immediately after a voice-engagement session ends (status COMPLETED) to assemble a priced proposal from the transcript's agreed changes and draft a matching personalized follow-up email in the same pass. Also applies the routing-rules check to decide whether the bundle goes to PENDING_REP_APPROVAL or PENDING_COMMS_APPROVAL. Trigger only when nextBestActionIdentified is non-null; if the session ended with no clear agreed change, do NOT invoke this skill — return the case to the queue for manual follow-up instead.
---

# Proposal Generation

Produces both the priced proposal and the matching email together — this is one agent action, not two separate hand-offs.

## Preconditions

- `VoiceSession.status = "COMPLETED"` and `nextBestActionIdentified` is non-null.
- Required disclosure checkpoints are verified `true` in `verifiedCheckpoints`.

## Proposal pricing

- `newMonthlyTotal` = current `MonthlyPremium` + rider premium delta.
- `addedFaceAmount` = rider's face amount if agreed.
- `oneClickLink` = simulated secure signature URL.

## Output shapes

```json
// ProposalDraft
{
  "proposalId": string, "caseId": string, "policyId": string,
  "riderAdded": string | null, "addedFaceAmount": number | null,
  "newMonthlyTotal": number, "oneClickLink": string,
  "generatedFromSessionId": string, "status": "DRAFTED"
}
