# Agentic Life & Health Policyholder Retention & In-Force Management System

An agentic policyholder retention platform built on Google Gemini, featuring a single root-agent orchestrator, runtime dynamic skill selection, single-writer state management, and responsive frontend screens designed per UI dashboard conventions.

---

## 🌟 Key Features

1. **Root Orchestrator & Dynamic Skills Catalog:**
   * Single-writer orchestrator engine (`orchestrator/server.py` & `invoke.py`) preventing race conditions.
   * Dynamic skill matching powered by Gemini LLM (`orchestrator/skill_selector.py`) reading frontmatter metadata from `.agent/skills/*/SKILL.md`.

2. **Flagship Policyholder Retention Journey:**
   * **Stage 1 (Signal & Classification):** Ingests life-event triggers (e.g. Michael Carter's address change + expired payment card) and tags policy archetypes (`Flight Risk`, `Buyer's Remorse`, `Low Lapse / Growth Candidate`).
   * **Stage 2 (Queue & Assignment):** Calculates priority scores (`$ Exposure × Urgency Weight`) and ranks servicing queue (#1 Michael Carter, $250k face amount, $42.5k cash value).
   * **Stage 3 (AI Voice Engagement):** Conducts autonomous AI voice call (`voice-engagement` skill), tracks running sentiment score (+0.85 positive), verifies compliance disclosures, and generates diarized transcript.
   * **Stage 4 (Proposal & Approval):** Generates priced proposal bundle (`Child Education Rider`, +$50,000 benefit, $485.00/mo) and transactional outreach email, presenting the **ACCEPT & SEND** human approval control point.

3. **Multi-Persona UI Screens:**
   * **Servicing Rep Console (`/`):** Priority Queue & Case Workspace.
   * **Chief Actuary Portfolio Analytics (`/portfolio-view`):** Read-only executive dashboard with KPI tiles, product type mix doughnut chart, archetype segment drilldowns, and 30-day simulated trajectory trend chart.
   * **Compliance Audit Trail Viewer (`/audit-view`):** Searchable audit log (`caseId`, `sessionId`, `proposalId`), expandable JSON inspectors, and reconstructed diarized voice call transcripts.

---

## 📁 Repository Structure
