# Policy Servicing & Retention Demo — Design Doc
### Antigravity root-agent + dynamic-skills rebuild

## 1. Overview

This covers the rebuild of the Policy Servicing, Retention & In-Force Management demo on Google Antigravity, replacing the prior ADK multi-agent build. The end user is an insurance-company Servicing Representative (plus secondary Chief Actuary and Compliance views) who needs to work a prioritized queue of at-risk/upside policies, let an AI voice agent handle the actual retention conversation, and review/approve the resulting proposal before it reaches the customer. The job to be done: convert a detected life-event or payment-risk signal into a retained or upsold policy, with a human accountable at exactly two points (triggering the engagement, approving the send) and never during the AI conversation itself.

This design doc is downstream of `Persona_Journeys_Automation_HITL_PRD_v2.docx` (business requirements, personas, state machine) and `Antigravity_Rebuild_Approach.md` (why ADK was replaced). It is the build-ready translation of both into screens, components, data, and the skill-invocation contract the root agent uses.

## 2. Design Rationale & UX Decisions

- **Decision:** One root orchestrator agent, zero autonomous sub-agents; capabilities live in on-demand Skills.
  **Because:** the ADK build's "agent conflicts" were a direct result of multiple agents holding independent state and writing to the same Case concurrently. A single reasoning loop with one writer per Case removes the race condition structurally, not by patching prompts.

- **Decision:** No agent tool-call trace or diagram as the primary UI on any rep-facing screen.
  **Because:** the prior build's UI looked like "a terminal with a diagram on the side" specifically because the agent trace *was* the UI. Reps need outcomes (story tag, transcript, proposal), not a debug view — the reasoning trace moves to a collapsed expander and to the separate Compliance/Audit screen.

- **Decision:** Story archetypes (Flight Risk, Buyer's Remorse, Low Lapse/Growth) are separate skill folders under `policyholder-insight/archetypes/`, not branches in one classifier prompt.
  **Because:** the stated requirement is "dynamic capability to add skills depending on the use case, and let the parent root agent figure it out" — a new archetype must be addable without touching orchestration code, which a folder-per-archetype structure satisfies directly.

- **Decision:** The Servicing Rep's live-call role is removed entirely; the Call Outreach Agent (via `voice-engagement`) conducts the full conversation autonomously.
  **Because:** this is a hard constraint from the finalized SOW (Gemini Live API, in-browser, no telephony, no human rep on the line) — it isn't a UX preference, it's the confirmed scope. The rep's touchpoints move to *before* (triggering) and *after* (reviewing transcript/sentiment/proposal).

- **Decision:** Two primary rep-facing screens only (Priority Queue, Case Workspace); Portfolio Dashboard and Audit viewer are secondary and built after the primary flow is validated.
  **Because:** the PRD's MVP scope and the SOW's demo scope both center on the single flagship journey — building four screens in parallel was called out as a risk (small review loop, easy to miss issues), so the design deliberately sequences them.

- **Decision:** A new `ENGAGEMENT_INITIATED` state sits between `ASSIGNED` and `IN_PROGRESS`.
  **Because:** unlike dialing a phone, an in-app AI voice session needs an explicit trigger separate from the session itself — this is also now the rep's only live decision point before the automated conversation runs, so it needed its own state to be visible and auditable.

## 3. Screens & Flows

### Priority Queue
- **Purpose:** let the rep see, at a glance, which case to work next and why.
- **Entry points:** rep login (default landing screen).
- **Exit points:** selecting a case → Case Workspace.
- **Layout / key elements:** a ranked list/table — `priority_rank`, story tag badge, urgency tier (P1/P2/P3), $ exposure, recommended action (or "needs assessment" if `fitScore` was too low to pre-fill one). Sorted by rank; no action controls beyond "open case."
- **States:** default (populated), empty ("No cases in your queue right now"), loading (skeleton rows).

### Case Workspace
The single most important screen — walks the rep through everything from context to send.

- **Purpose:** review context, trigger the AI engagement, then review and approve its output.
- **Entry points:** from Priority Queue.
- **Exit points:** Accept & Send → case leaves active view (→ `CUSTOMER_ACTION`); or, on a dropped/partial session, back to the queue flagged for follow-up.
- **Layout / key elements**, top to bottom:
  1. **Context panel:** policyholder name, story tag, fit score, recommended action, tenure, dependents — read-only.
  2. **Engagement control:** a single prominent "Start AI Voice Engagement" button (state: `ASSIGNED`). Once clicked, case moves to `ENGAGEMENT_INITIATED` then `IN_PROGRESS` — this is the rep's one live decision.
  3. **Live status (while `IN_PROGRESS`):** a simple "Engagement in progress…" indicator with a live sentiment readout — not a transcript stream, since no one needs to watch it live (no human is required on the call).
  4. **Post-engagement summary (once `PROPOSAL_DRAFTED`/`OUTREACH_DRAFTED`):** diarized transcript (collapsible), sentiment trend chart, verified-checkpoints checklist, proposal terms card, email preview card.
  5. **Accept & Send:** the single highest-contrast control on the screen, only enabled once both proposal and email are present and required disclosures are verified.
  6. **"Why this?" expander:** collapsed by default — shows the Chain-of-Thought reasoning for anyone who wants it, never shown unprompted.
- **States:** `ASSIGNED` (context only, engagement button enabled), `IN_PROGRESS` (live status), `PROPOSAL_DRAFTED`/`OUTREACH_DRAFTED`/`ROUTED` (review state), `PARTIAL`/`DROPPED` (explicit banner: "Engagement incomplete — returned to queue for follow-up"), `PENDING_REP_APPROVAL` (Accept & Send enabled), `SENT` (confirmation, case about to leave active view).

### Portfolio Dashboard (secondary)
- **Purpose:** portfolio-level view for the Chief Actuary.
- **Layout:** KPI tiles (in-force $, lapse-risk exposure $, retention opportunity $) → product mix → segment drill-down table → trend chart (labeled simulated per `portfolio-intelligence` skill's output).
- **States:** empty segment ("No policies currently match this story"), populated, loading.

### Audit Trail Viewer (secondary)
- **Purpose:** Compliance's end-to-end reasoning trace — the one screen where the trace *is* the content.
- **Layout:** searchable by `caseId`/`sessionId`/`proposalId`; chronological list of `AuditEntry` records including the full voice-session transcript.
- **States:** empty (no matching case), populated.

## 4. Component Inventory

| Component | Used in screens | Variants / states | Notes |
|---|---|---|---|
| Story Tag Badge | Priority Queue, Case Workspace, Portfolio Dashboard | Flight Risk / Buyer's Remorse / Low Lapse-Growth / none | Color-coded per `ui-dashboard-conventions`; not alarmist-red by default |
| Urgency Pill | Priority Queue | P1-High / P2-Medium / P3-Low | |
| Case Card / Row | Priority Queue | default, needs-assessment (no recommendedAction) | |
| Engagement Status Indicator | Case Workspace | not started / in progress / completed / partial / dropped | Drives which section of the Case Workspace is visible |
| Sentiment Trend Chart | Case Workspace, Audit Viewer | — | Simple line/area, -1..1 |
| Transcript Viewer | Case Workspace (collapsed), Audit Viewer (expanded) | collapsed / expanded | Same component, different default state |
| Proposal Summary Card | Case Workspace | drafted / pending-approval / sent | |
| Email Preview Card | Case Workspace | drafted / pending-approval / sent | |
| Accept & Send Button | Case Workspace | enabled / disabled (missing disclosure or incomplete draft) | Highest-contrast control on its screen |
| "Why this?" Reasoning Expander | Case Workspace, Portfolio Dashboard | collapsed (default) / expanded | Never auto-expanded |
| KPI Tile | Portfolio Dashboard | — | |
| Segment Drilldown Table | Portfolio Dashboard | populated / empty | |
| Empty State Banner | all screens | — | Consistent copy pattern: "No [x] currently [y]" |

## 5. Data Model
