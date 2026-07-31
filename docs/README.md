# Documentation — the whole engagement, every step

This folder documents the complete `launch-engagement` pipeline: every phase the
orchestrator runs, and every step of each child skill and procedure it delegates to.
Read [00_pipeline_overview.md](00_pipeline_overview.md) first — it is the one-page map;
each phase page then spells out that phase's full procedure, artifacts, gates, and the
split between what the agent does and what stays human.

| Page | Covers |
|---|---|
| [00_pipeline_overview.md](00_pipeline_overview.md) | The full chain, delivery lanes, automation posture, gate design principles |
| [01_intake.md](01_intake.md) | The typed intake contract, validator, state persistence |
| [02_phase_0_scaffold.md](02_phase_0_scaffold.md) | Project scaffold: dossier, runbooks, deliverable stubs |
| [03_phase_1_discovery.md](03_phase_1_discovery.md) | Situation assessment: fact base, evidence rules, approval gate |
| [04_phase_2_kpi_design.md](04_phase_2_kpi_design.md) | Decision-linked KPI system and its validation contract |
| [05_phase_3_kit_deploy.md](05_phase_3_kit_deploy.md) | Kit deploy, requirements hydration, milestone-gated tracker |
| [06_phase_4_build.md](06_phase_4_build.md) | The report-as-code build: design-first UI spec (Figma or mockup), TMDL model, PBIR visuals, Skills-for-Fabric and Deneb routes, evidence gate |
| [07_phase_5_qa.md](07_phase_5_qa.md) | Model and report QA checklists, DAX regression tests, security evidence |
| [08_phase_6_handoff.md](08_phase_6_handoff.md) | Measure dictionary, client package, citation receipt, delivery manifest |
| [09_phase_7_readout.md](09_phase_7_readout.md) | Executive narrative, decision memo, readout deck, case study |
| [10_phase_8_value.md](10_phase_8_value.md) | Value ledger, ownership, governance |
| [11_phase_9_close.md](11_phase_9_close.md) | Closeout, retrospective, operations log, tracker reconcile |
| [12_cross_cutting.md](12_cross_cutting.md) | verify-build, the citation gate, state machine, resume rules, trust boundaries |

Two reading notes:

- **This is the specification of the whole system**, including parts whose code lives
  only in the private vault (the repository's runnable extract covers the intake
  pipeline and Phase 0; later-phase runners, kit templates, and sibling skills are
  documented here but not all included as code).
- **Automation posture is explicit.** Every step is agent-ready, hybrid, or a
  deliberate manual wall; the seams that stay human (approvals, desktop clicks, client
  sign-off) are design decisions, not gaps.
