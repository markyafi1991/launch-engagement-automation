# Launch-Engagement Automation

An orchestration engine designed to run a full AI/BI consulting engagement end-to-end — from
a structured intake through scaffolding, discovery, KPI design, kit deployment, build, QA,
handoff, readout, value realization, and close — by chaining a pack of single-purpose
delivery skills in strict phase order.

This repository is a sanitized extract of one subsystem from a larger private
operations vault. It pairs the automation's **source code** with the **multi-tool
governance audit** the automation is held to.

## Status: Beta

**Beta** is the honest label for where this stands: built, reviewed by six independent AI
reviewer seats, and **not yet run on a live engagement**. It is not a placeholder for
"nearly v1" — the version only moves when the milestone below is actually met.

The Pack is one versioned product. The automation, this repository, the audit board, and the
published write-up all carry the same number; they never advertise different versions.

| Milestone | What earns it | State |
|-----------|---------------|-------|
| **Beta** | Built and multi-reviewer audited; not yet run on a live engagement | **Current** |
| v1 | The first engagement run end to end | Next |
| v1.x | Each audit round that lands changes | — |
| v2 | A structural change to the phase chain or gate model, by definition, regardless of diff size | — |

`v2.x` applies the `v1.x` rule on the v2 line; the pattern is `<major>.<audit-round>`.

## What is in this repository

Read this before cloning. This is a sanitized extract, and its runnable surface is
deliberately narrower than the pipeline it documents.

- **Runnable here:** the **intake pipeline** and **Phase 0 (scaffold)**. The intake pipeline is
  fully self-contained and exercised by the test suite below. The Phase 0 scaffold code ships
  as well, but the vault templates it consumes do not — which is why four tests skip.
- **Documented here, not runnable here:** **Phases 1 through 9**. The [`docs/`](docs/) folder
  specifies each of those phases — procedures, gates, and the agent-vs-human split — but the
  executing code for them is not shipped in this extract.
- **Size of the extract:** the private `launch-engagement` skill carries **41 script
  modules**; the copy in this repository ships **7**.
- **Known limitation of the extract:** `scripts/engagement_constants.py` here writes a single
  shared state file (`.engagement_state.json`, schema `1.0`) at the repository root, so a
  second engagement would overwrite the first. The private tree replaced that with
  per-engagement state files plus an index. It is named here rather than hidden.

In short: you can clone this, validate an intake, run the tests, and read the full pipeline
specification. You cannot run a complete nine-phase engagement from it.

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

Of that table, **Intake and Phase 0 ship as runnable code in this repository**. Phases 1
through 9 are specified in [`docs/`](docs/) and executed by the private tree.

The design principle: every phase is either **agent-ready**, **hybrid**, or a deliberate
**manual wall** (a human-in-the-loop seam that is kept human on purpose — for example,
client sign-off or a licensed modeling click).

**Full pipeline documentation:** the [`docs/`](docs/) folder walks the entire
engagement — every phase, every child-skill procedure, every gate, and the explicit
agent-vs-human split — starting from
[docs/00_pipeline_overview.md](docs/00_pipeline_overview.md).

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
├── tests/                       # 24 tests (unittest)
└── examples/                    # sample intakes (client + portfolio)
scripts/engagement_constants.py  # shared enums (also used by start-project)
```

## Run the tests

The intake pipeline is self-contained and testable from a fresh checkout:

```bash
python3 -m unittest discover -s .claude/skills/launch-engagement/tests -p "test_*.py"
```

Expected: `Ran 24 tests ... OK`. Cross-skill integration tests require the live
Phase 0 scaffold against templates that live in the private vault and are not included here.

## The audit

Building the automation is half the story. The other half is holding it to an engineering
bar. The [`audit/`](audit/) folder documents a **six-reviewer, eleven-phase governance
audit**: each phase is independently reviewed by six different AI engineering agents, each
wearing a distinct hat (technical integrity, architecture, maintainability, repository
standards, adversarial red-team, and a final principal-engineer ship call), then signed off
by a human.

All eleven phases have been through all six agent seats at the Beta target. **None carries
owner sign-off yet** — owner sign-off is what "verified" means here, and its absence is
precisely why this is Beta and not v1. Round 1 of the audit produced thirteen findings:
seven became proposed cross-cutting control points scheduled across v1, v1.x, and v2, and
the remaining six were folded into the phase rows they belong to.

See [audit/README.md](audit/README.md) for the methodology, the reviewer prompts, and the
**live, honest status board** — the audit is in progress, and the board shows exactly how
far along it is rather than claiming more than has been done.

---

## Notes on scope and data

- **Extracted, not the whole system.** This is one subsystem lifted out of a larger private
  vault, and only part of that subsystem — see [What is in this
  repository](#what-is-in-this-repository) above. Some referenced templates, SOPs, and
  sibling skills are intentionally not included; the code that is here runs and is tested on
  its own.
- **No real client data.** Everything here is synthetic or structural. Example intakes are
  fictional.
- **Sanitized.** Internal identifiers, workspace links, and local paths have been removed.

## License

[MIT](LICENSE).
