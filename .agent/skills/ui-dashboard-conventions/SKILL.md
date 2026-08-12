---
name: ui-dashboard-conventions
description: Load this skill BEFORE writing or modifying any screen in the Servicing/Selling Agent console or portfolio dashboard — Priority Queue, Case Workspace, Portfolio Dashboard, or the Audit viewer. Defines the shared design tokens, layout hierarchy, and the "outcomes before agent internals" rule that keeps every screen visually and structurally consistent. This is the direct fix for the prior build looking like a terminal with a diagram on the side — do not skip it to save a step.
---

# UI Dashboard Conventions

Read this once per new screen, before generating any UI code. See also: `/mnt/skills/public/frontend-design/SKILL.md` for general visual-design guidance — this skill is the project-specific layer on top of that.

## The one rule that matters most

**Never show raw agent tool-call logs or a live agent trace as the primary UI.** Show outcomes: story tag, transcript, sentiment, proposal terms, queue rank. If someone wants to see the reasoning behind a decision, put it behind a small, clearly-labeled "Why this?" expander — collapsed by default, never the main view. This single rule is what separates a product from a debug console.

## Information hierarchy per persona

- **Servicing Rep, Priority Queue:** rank → story tag → dollar exposure → recommended action, in that order, left to right or top to bottom. Nothing about *how* the system decided this belongs above the fold.
- **Servicing Rep, Case Workspace:** context (who, story, why) → engagement status (not started / in progress / completed) → transcript + sentiment (once available) → proposal + email side by side → Accept & Send as the single most visually prominent control on the screen.
- **Chief Actuary, Portfolio Dashboard:** KPI tiles first (in-force $, lapse exposure $, retention opportunity $), segment breakdown second, trend charts third. Read-only — no action controls on this screen at all.
- **Compliance, Audit viewer:** this is the *one* screen where the reasoning trace is the primary content — but it's a separate, clearly-labeled secondary screen, never the default view for a rep or actuary.

## Design tokens

| Token | Use |
|---|---|
| Urgency P1 | High-attention accent color, used sparingly (badge/pill only, never a full-screen background) |
| Urgency P2 / P3 | Neutral/muted, receding relative to P1 |
| Story tag badges | One consistent shape/style per tag (Flight Risk, Buyer's Remorse, Low Lapse/Growth) — color-coded but not alarmist (no default-red for every risk tag; reserve strong red for genuinely urgent states) |
| Sentiment trend | Simple line or area chart, -1 to 1 scale, plotted against transcript timestamps |
| Accept & Send | The single highest-contrast, most prominent button on its screen — this is the compliance control point and should look like one |

## States every screen needs (only where relevant)

- **Empty:** explicit, friendly text ("No policies currently match this story" / "No cases in your queue right now") — never a blank panel.
- **Loading:** skeleton/placeholder, not a spinner-only screen for anything that takes more than ~1s (e.g., a voice session in progress should show live status, not a generic loader).
- **Error / Partial:** for a dropped voice session, show the PARTIAL status plainly on the Case Workspace with a clear next step ("Returned to queue for follow-up"), not a silent disappearance.

## Consistency check before shipping a screen

Before finishing any screen, confirm: (1) no raw tool-call trace is visible by default, (2) the primary action for that persona is the most visually prominent element, (3) empty/loading/partial states are handled, not just the happy path, (4) it uses the same badge/color tokens as every other screen already built — don't invent a new visual language per screen.
