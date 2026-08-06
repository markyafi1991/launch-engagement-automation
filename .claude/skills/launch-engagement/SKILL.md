---
name: launch-engagement
description: Orchestrate a full AI/BI client or portfolio engagement by chaining the Project Delivery skill pack — scaffold, discovery, KPI design, kit deploy, build runbook, QA, readout, and close. Use when the user says "/launch-engagement", "launch engagement", "run the full project", "walk me through the engagement", "start to finish on this project", or wants the complete project-delivery chain instead of a single skill. Scoped to engagement and portfolio content only. Composes with /start-project, /project-kit, and the engagement template; does not replace them.
---

## Scope of this copy — sanitized extract

This file is published as part of a sanitized extract of one subsystem from a larger private
operations vault. Only part of the pipeline it describes ships here as code.

- **Runnable here:** the **intake pipeline** and **Phase 0 (scaffold)** — `validate_intake.py`
  and the modules beside it, plus `start-project`'s `build_project.py`. These are tested and
  work from a fresh checkout.
- **Not included:** the **Phase 1–9 gate runners**. The per-phase contracts, evidence
  generators, hash-bound gate files, and TTY approval prompts that actually enforce those
  phases live in the private tree. Phases 1–9 are described below and documented in `docs/`,
  but there is nothing in this repository to invoke for them.

Read the phase sections that follow — **the Phase 3–9 sections in particular** — as a summary
of the procedure, not as the enforcement. They state what each phase does and what its gate
means; they are not backed by executable gate machinery in this copy. An operator working from
this repository alone runs those phases by hand.

## Before proceeding

Read `01_Operations/Skill Notes/launch-engagement - Owner Notes.md` if it exists, and
Project Delivery Pack. Treat owner highlights and `[!owner-*]` callouts as required context.

# Launch Engagement

Walk the **Project Delivery Pack** (Project Delivery Pack) end-to-end. This skill is the
*orchestrator* — it chains existing skills in phase order. It does not duplicate their procedures;
at each phase, read that skill's `SKILL.md` and owner companion note, then execute it.

Pattern: Skill Packs Hub. Engagement spine: AI-BI Consulting Engagement — Template Guide.
Worked example: Variance Pack.

## Guardrails

- Engagement scope only — the skill reads and writes engagement content, never unrelated areas of the source vault.
- Portfolio projects: data classification must be `synthetic` or `public`.
- Never put real client data into `04_Portfolio/`.
- Software/code builds → **Linear**, not ClickUp Portfolio Projects (code-vs-tool, not topic).
- Pause at human-in-the-loop seams (Power BI Desktop clicks, client sign-off, credential entry).
- Run `/verify-build` before reporting any phase done; run `/cite check` before external narrative ships.
- Log substantive work in today's daily note per CLAUDE write protocol.

## Intake (before Phase 0)

Collect or confirm the required intake fields, then run the validator before Phase 0. Do not proceed on
prompt judgment alone. Missing optional fields receive sensible defaults.

**Glossary:** `delivery_lane` = where execution is tracked (ClickUp BI lane, Linear, or advisory ClickUp).
`engagement_type` = service shape (`analytics`, `automation`, `advisory`).

### Field contract

| JSON field | Requirement | Default | Notes |
|---|---|---|---|
| `kind` | **Required** | — | `client` or `portfolio` |
| `name` | **Required** | — | Engagement / project name (no path separators) |
| `delivery_lane` | **Required** | — | `tool-built-bi` (Power BI + future BI kits), `software-code`, or `advisory-only` |
| `kit` | Conditional | — | Required when `delivery_lane` is `tool-built-bi`; must match a kit manifest `kit` name |
| `source` | Conditional | — | Required when `kind` is `client` (CRM acquisition source, e.g. `Upwork`) |
| `industry` | Optional | `""` | Passed through to `/start-project` |
| `engagement_type` | Optional | `analytics` | `analytics`, `automation`, or `advisory` |
| `data_classification` | Optional | `internal` (client) / `synthetic` (portfolio) | Portfolio allows only `synthetic` or `public` |
| `deliverables` | Optional | `["Dashboard"]` | Array of short deliverable descriptions |
| `project_path` | Optional | `02_Clients/<name>` or `04_Portfolio/<name>` | Must stay under the correct area; cannot point into confidential subfolders |
| `starting_phase` | Optional | `0` | Resume point (0–9); validator checks prior-phase artifacts exist |
| `status` | Optional | `prospect` (client) / `active` (portfolio) | Client CRM status |
| `include_portfolio_readout` | Optional | `false` | When `true`, portfolio builds keep Phase 7 (readout / case-study) |

JSON schema: `.claude/skills/launch-engagement/intake.schema.json` (reference/documentation — the
validator enforces the same rules in code; a test guards the two against drift). Copy-paste examples:
`examples/portfolio_tool_bi.json`, `examples/client_tool_bi.json`, `examples/portfolio_software_code.json`.
`examples/resume_phase_1.json` is an illustrative resume payload — it only validates against a vault where
the Phase 0 artifacts in the resume matrix below already exist.

Portfolio builds skip Phase 7 by default unless `include_portfolio_readout` is `true`.

### Validate

Write a temporary payload (e.g. `intake.json` at vault root — gitignored) or use `--json` / stdin:

```bash
python3 .claude/skills/launch-engagement/scripts/validate_intake.py \
  --file intake.json
```

Minimal portfolio example:

```json
{
  "kind": "portfolio",
  "name": "Project Name",
  "delivery_lane": "tool-built-bi",
  "kit": "Power BI Project Kit"
}
```

Client example:

```json
{
  "kind": "client",
  "name": "Acme Funds",
  "delivery_lane": "tool-built-bi",
  "kit": "Power BI Project Kit",
  "source": "Upwork",
  "data_classification": "financial"
}
```

The validator normalizes inputs, applies defaults, verifies resume readiness (when `starting_phase > 0`),
detects whether Phase 0 should `create`, `sync_existing`, or `load_existing`, and persists output to
**`.engagement_state.json` at the vault root** (gitignored — not `.cache/`). Emitted
`start_project_command` values are always of the form
`build_project.py create|sync --state-file .engagement_state.json` (metadata lives in the
state file). Use that command when `phase0_action` is `create` or `sync_existing`; when it is
`load_existing`, the command is intentionally empty. Use `kit_deploy_dry_run_command` for
Phase 3. The `phases` array is the lane-filtered execution plan.

**Resume artifact matrix** (validator-enforced): Phase 1 → dossier + folder + `SOP Runbook.md` +
`Engagement_Runbook.md` + `Deliverables/00_Statement_of_Work.md` +
`Deliverables/00_Brand_and_Design_System.md`; Phase 2 → `Deliverables/01_Situation_Assessment.md`;
Phase 3 → `Deliverables/02_KPI_Design.md`; Phase 4 (tool-built-bi) →
`<kit deploy_root>/AI Build Runbook.md`; Phase 5 (tool-built-bi) → `<kit deploy_root>/Build Recipe (TEMPLATE).md`.
Kit folder names come from each kit's `manifest.json` `deploy_root` field.

Script docs: `.claude/skills/launch-engagement/scripts/README.md`.

## Orchestration flow

Act as a **step-by-step orchestrator**. Report the current phase, delegate to the child skill,
verify, then advance only after confirmation or objective DoD met.

### Phase 0 — Scaffold

**If** project folder + dossier do not exist → run **`/start-project`** (read its SKILL.md first).
Use the validator's normalized `start_project_command`; it includes `--project-path` so the path
collected during intake is honored instead of inferred differently.

**If** they exist → load the dossier and `SOP Runbook.md`; confirm metadata.

**Client only (Phase 0 deliverables):** work SOW, brand, and kickoff per the engagement runbook
(`Deliverables/00_*`, kickoff charter). Link vault SOPs; do not edit canonical SOPs.

**Register:** both → daily log. Client CRM pipeline row and Portfolio Hub linking remain
**manual** (same as `/start-project`): Clients Hub auto-surfaces dossiers via Dataview;
Portfolio Hub is curated by hand.

### Phase 1 — Discovery

Run **`/situation-assessment`** → `Deliverables/01_Situation_Assessment.md` (or equivalent).
Label fact / interpretation / assumption. End with diagnostic questions.

**Gate:** owner confirms the situation read is sufficient before KPI design.

### Phase 2 — KPI design

Run **`/kpi-architect`** → decision-linked KPI table in the engagement runbook / requirements doc.

**Gate:** KPIs tied to decisions the report must drive (not a field dump).

### Phase 3 — Kit deploy + ClickUp

Only enter this phase when validated `delivery_lane` is `tool-built-bi`. Software/code builds route
to Linear and advisory-only work skips kit deploy. Run **`/project-kit`** (read its SKILL.md +
target kit's Kit Guide):

1. Draft `Dashboard_Requirements` and `Build Recipe` from intake answers.
2. Use the validator's normalized `kit_deploy_dry_run_command` → confirm → live deploy.
3. Create ClickUp list in Portfolio Projects → matching **type folder** (Power BI first).
   Build the **full milestone tree** per SOP - Milestone-Driven ClickUp Project Setup —
   source the **engagement runbook milestone arc** (11 gates), not just AI Build Runbook phases.
4. Stamp list + milestone IDs into the project dossier / `_Project Index`.

**Optional:** `/task-reconcile` after ClickUp push.

**Advisory-heavy:** optionally run `/stakeholder-alignment` or `/business-case-builder` before build.

### Phase 4 — Build (runbook)

Open the deployed **AI Build Runbook** (e.g. `<project>/Power BI Kit/AI Build Runbook.md`).
Walk phases 0–7 sequentially:

- **Agent tasks:** synthetic data, PBIP scaffold, TMDL, DAX, tests, PBIR visuals.
- **Human tasks:** pause for Desktop preview features, refresh, visual QA — wait for explicit confirmation.

Record steps in `Build Recipe (TEMPLATE).md`.

### Phase 5 — QA

1. Kit checklists (`Model_Build_QA_Checklist`, `Report_Polish_and_Handoff_Checklist`).
2. Run **`/verify-build`** with an explicit definition of done (open report, re-run numbers, tests green).
3. Report **verified, not just asserted**.

### Phase 6 — Handoff package

- Fill `Measure_Dictionary`, handoff docx (`Dashboard_Documentation_Handoff_v2.docx`, `Delivery_Checklist_v2.docx`).
- Run **`/cite check`** on any external-facing narrative before it ships.

### Phase 7 — Readout (client / case-study)

Run **`/narrative-builder`** → **`/decision-memo`** → executive readout deck per
SOP - Executive Readout Deck.

Portfolio: optional case-study pass into `Portfolio_Case_Study_Template_v2.docx` — still `/cite check`.

### Phase 8 — Value

Run **`/value-realization`** → value ledger + "how to read it" one-pager.

### Phase 9 — Close

- Closeout SOP (SOP - Engagement Closeout & Retrospective): acceptance, invoice pointer, retro.
- Append **`/daily-log`** entry covering every auditable path changed this session.
- **`/task-reconcile`** if ClickUp state changed.

## Resume / partial runs

Set `starting_phase` in the intake payload (see Intake section). The validator checks that required
prior-phase artifacts exist before allowing the resume. Read `.engagement_state.json` or the
validator stdout for the lane-filtered `phases` array. Load the dossier, engagement runbook, and ClickUp
list state before continuing. Never re-deploy a kit with `--force` without owner approval.

**Lane resume boundaries:** `software-code` engagements cannot resume into the kit phases (3–6, which route
to Linear rather than this orchestrator); resume them at phase 0–2 or 7–9. The readiness matrix gates
resumes only through Phase 5 artifacts — resuming at 6–9 assumes later-phase outputs are managed by hand.

## Close-out

Report:

- Phases completed and next phase
- Project path, dossier, kit version (if deployed)
- ClickUp list URL + stamped IDs
- Verification method for each completed gate
- Open risks or deferred items

Do not register a Cadence trigger until the owner battle-tests a full engagement unparked.
