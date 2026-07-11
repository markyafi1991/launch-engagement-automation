# Launch-Engagement Automation

An orchestration engine that runs a full AI/BI consulting engagement end-to-end — from a
structured intake through scaffolding, discovery, KPI design, kit deployment, build, QA,
handoff, readout, value realization, and close — by chaining a pack of single-purpose
delivery skills in strict phase order.

This repository is a sanitized extract of one subsystem from a larger private
operations vault. It pairs the automation's **source code** with the **multi-tool
governance audit** the automation is held to.

---

## What it does

`launch-engagement` is an *orchestrator*, not a monolith. It does not re-implement each
delivery step; it validates a single engagement intake, then drives the existing
delivery skills phase by phase:

| Phase | Step | Engine |
|-------|------|--------|
| Intake | Parameterize the engagement | `validate_intake.py` JSON contract → normalized state |
| 0 | Scaffold | `build_project.py create\|sync` + engagement template |
| 1 | Discovery | Situation assessment → sign-off gate |
| 2 | KPI design | Decision-linked KPI table |
| 3 | Kit deploy | Project-kit deploy + work-surface milestone tree |
| 4 | Build | Report-as-code (PBIP/TMDL/DAX), human at the modeling seam |
| 5 | QA | Checklists + explicit definition-of-done |
| 6 | Handoff | Measure dictionary + handoff package + citation gate |
| 7 | Readout | Narrative → decision memo → executive deck |
| 8 | Value | Value ledger + how-to-read-it one-pager |
| 9 | Close | Closeout + retrospective + reconcile |

The design principle: every phase is either **agent-ready**, **hybrid**, or a deliberate
**manual wall** (a human-in-the-loop seam that is kept human on purpose — for example,
client sign-off or a licensed modeling click).

## The intake contract

The heart of the runnable code is a typed intake pipeline that refuses to start a build on
loose prompt judgment. It:

- validates a JSON intake against a schema (`intake.schema.json`),
- normalizes and applies sensible defaults to optional fields,
- runs readiness checks, and
- emits the exact downstream commands (scaffold, kit-deploy dry-run) for Phase 0 and Phase 3.

```
.claude/skills/launch-engagement/
├── SKILL.md                     # the orchestrator specification
├── intake.schema.json           # the intake JSON contract
├── scripts/
│   ├── validate_intake.py       # entry point: validate → normalize → emit commands
│   ├── intake_schema.py         # typed intake model
│   ├── intake_normalize.py      # defaults + normalization
│   ├── intake_readiness.py      # readiness checks
│   ├── intake_commands.py       # emits start-project / project-kit commands
│   ├── kit_registry.py          # portfolio kit registry
│   └── _paths.py                # import bootstrap
├── tests/                       # 26 tests (unittest)
└── examples/                    # sample intakes (client + portfolio)
scripts/engagement_constants.py  # shared enums (also used by start-project)
```

## Run the tests

The intake pipeline is self-contained and testable from a fresh checkout:

```bash
python3 -m unittest discover -s .claude/skills/launch-engagement/tests -p "test_*.py"
```

Expected: `Ran 26 tests ... OK (skipped=4)`. The skipped tests exercise the live
Phase 0 scaffold against templates that live in the private vault and are not included here.

## The audit

Building the automation is half the story. The other half is holding it to an engineering
bar. The [`audit/`](audit/) folder documents a **five-reviewer, eleven-phase governance
audit**: each phase is independently reviewed by five different AI engineering agents, each
wearing a distinct hat (technical integrity, architecture, maintainability, repository
standards, and a final principal-engineer ship call), then signed off by a human.

See [audit/README.md](audit/README.md) for the methodology, the reviewer prompts, and the
**live, honest status board** — the audit is in progress, and the board shows exactly how
far along it is rather than claiming more than has been done.

---

## Notes on scope and data

- **Extracted, not the whole system.** This is one subsystem lifted out of a larger private
  vault. Some referenced templates, SOPs, and sibling skills are intentionally not included;
  the code that is here runs and is tested on its own.
- **No real client data.** Everything here is synthetic or structural. Example intakes are
  fictional.
- **Sanitized.** Internal identifiers, workspace links, and local paths have been removed.

## License

[MIT](LICENSE).
