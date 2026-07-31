# Pipeline overview — the whole engagement in one map

`launch-engagement` runs a complete AI/BI consulting engagement as a strict phase chain.
Each phase delegates to a single-purpose child skill or runbook, verifies an objective
gate, and only then advances. This page is the master map; each phase has its own page
with every step spelled out.

## The chain

```
Intake  ->  Phase 0   ->  Phase 1    ->  Phase 2    ->  Phase 3     ->  Phase 4  ->  Phase 5  ->  Phase 6  ->  Phase 7  ->  Phase 8  ->  Phase 9
(validate)  Scaffold      Discovery      KPI design     Kit deploy      Build        QA           Handoff      Readout      Value        Close
```

| Phase | Name | Engine (child skill / runbook) | Machine gate artifact | Doc |
|---|---|---|---|---|
| — | Intake | `validate_intake.py` JSON contract | `.engagement_states/<digest>.json` | [01_intake.md](01_intake.md) |
| 0 | Scaffold | `start-project` (`build_project.py`) | Phase 0 content floor (non-empty, no `{{placeholder}}`) | [02_phase_0_scaffold.md](02_phase_0_scaffold.md) |
| 1 | Discovery | `situation-assessment` + `discovery.py` | `01_Situation_Assessment.gate.json` + owner approval | [03_phase_1_discovery.md](03_phase_1_discovery.md) |
| 2 | KPI design | `kpi-architect` + KPI runner | `02_KPI_Design.gate.json` + owner approval | [04_phase_2_kpi_design.md](04_phase_2_kpi_design.md) |
| 3 | Kit deploy + work surface | `project-kit` + ClickUp provisioner | `phase3.gate.json` + `clickup_receipt.json` | [05_phase_3_kit_deploy.md](05_phase_3_kit_deploy.md) |
| 4 | Build (report as code) | AI Build Runbook (PBIP/TMDL/DAX/PBIR) | `phase4.evidence.json` + `phase4.gate.json` | [06_phase_4_build.md](06_phase_4_build.md) |
| 5 | QA | QA runner + DAX Query View tests | `phase5.dod.json` + `phase5.gate.json` | [07_phase_5_qa.md](07_phase_5_qa.md) |
| 6 | Handoff package | Handoff runner + Measure Dictionary | `phase6.dod.json` + receipts + `phase6.gate.json` | [08_phase_6_handoff.md](08_phase_6_handoff.md) |
| 7 | Readout | `narrative-builder` + `decision-memo` + deck | `phase7.dod.json` + `phase7.gate.json` | [09_phase_7_readout.md](09_phase_7_readout.md) |
| 8 | Value | `value-realization` | Value ledger + one-pager | [10_phase_8_value.md](10_phase_8_value.md) |
| 9 | Close | Closeout SOP + `daily-log` + `task-reconcile` | Closeout record | [11_phase_9_close.md](11_phase_9_close.md) |

Cross-cutting controls (`verify-build`, the citation gate, state debugging, resume rules,
trust boundaries) are documented in [12_cross_cutting.md](12_cross_cutting.md).

## Delivery lanes

The intake's `delivery_lane` filters which phases run:

- **`tool-built-bi`** — the full chain above. Phases 3-6 are the Power BI kit phases.
- **`software-code`** — phases 3-6 are skipped; execution routes to the engineering
  tracker (Linear) instead of the kit. Resume cannot enter phases 3-6.
- **`advisory-only`** — phases 3-6 are filtered out of the plan entirely.

Portfolio engagements skip Phase 7 (readout) by default unless
`include_portfolio_readout: true`.

## Automation posture: agent-ready, hybrid, manual wall

Every step in the pipeline is classified one of three ways. This is deliberate: the goal
is "as automated as possible," with the seams that stay human kept human on purpose.

| Posture | Meaning | Examples |
|---|---|---|
| Agent-ready | The agent executes it end to end | TMDL model text, DAX measures, PBIR visual JSON, synthetic data, theme, docs scaffolds, intake validation, state machine |
| Hybrid | Agent authors, human applies or confirms | Applying model/report edits into an open Power BI Desktop (restart/refresh), data refresh and credential entry, running PowerShell test harnesses, publishing |
| Manual wall | Human by design | Owner approvals at every gate (interactive TTY secret), client sign-off, final visual-polish judgment, enabling preview features, anything touching real client data classification |

## The build automation stack (Phase 4)

The report itself is built as code because the PBIP project format is plain text — the
semantic model is TMDL and every visual is a PBIR JSON file. Four authoring layers stack:

1. **Design-first UI spec** — a high-fidelity dashboard design (Figma via MCP, or a
   low-fidelity HTML mockup) locked before any build; the build executes a decided
   layout instead of art-directing live in Power BI.
2. **Semantic model** — TMDL authored directly, or through the Power BI Modeling MCP
   server (tables, relationships, calendar, measures).
3. **Report pages** — either the Microsoft Skills-for-Fabric chain (report planner ->
   report designer -> report authoring, self-validating with desktop-bridge screenshots)
   or direct PBIR JSON authoring per visual.
4. **Non-native visuals** — Deneb (Vega-Lite) and HTML-Viewer specs written by the agent
   for visuals Power BI lacks (bullet charts, variance KPI cards, benchmarking dots).

Known seams (recorded honestly, not hidden): the Modeling MCP edits the model but not
report pages; Skills-for-Fabric cannot yet author KPI-card reference labels (undocumented
visual internals — the Deneb route is the workaround); editor TMDL/PBIR edits are not
reflected live in an open Desktop (restart to reload).

## Gate design principles

- **Fail closed.** Missing evidence, placeholder text, hollow artifacts, or stale hashes
  block the phase; nothing is auto-forged.
- **Hash binding.** Approvals bind to a semantic SHA-256 of the artifact plus the intake
  hash; any post-approval edit invalidates the gate and requires re-validation and
  re-approval. Approvals expire after 14 days on resume.
- **Evidence over assertion.** Validation output is parsed for failure language ("3
  passed, 2 failed" is rejected); attestations are explicit CLI flags, never defaults;
  human checkpoints must cite the SHA-256 of the evidence they reviewed.
- **Honest trust boundaries.** Each gate documents what the machine actually verifies
  versus what remains human attestation (for example, the runner verifies DAX result
  JSON shape and hashes; it does not open Power BI Desktop itself). The interactive
  owner-secret prompt is an audit deterrent, not cryptographic authentication.
