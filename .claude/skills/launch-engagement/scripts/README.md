# launch-engagement scripts

Canonical skill tree: `.claude/skills/launch-engagement/`. The `.agents/skills/launch-engagement/` copy must stay in sync (tests assert key files match).

## Intake validator (Phase 0 gate)

Validates and normalizes intake JSON before Phase 0. Writes normalized state to
**`.engagement_state.json`** at the vault root (gitignored). Downstream
`/start-project` create/sync commands consume that file via `--state-file`.

The emitted `phase0_action` is `create`, `sync_existing`, or `load_existing`:

| `phase0_action` | Meaning | `start_project_command` |
|---|---|---|
| `create` | No dossier / folder / SOP runbook yet | `build_project.py create --state-file .engagement_state.json` |
| `sync_existing` | Legacy scaffold (dossier + folder + SOP runbook) missing Phase 0 deliverables | `build_project.py sync --state-file .engagement_state.json` |
| `load_existing` | Phase 0 machine artifacts already present | empty list (noop) |

```bash
# From vault root — file input
python3 .claude/skills/launch-engagement/scripts/validate_intake.py \
  --file .claude/skills/launch-engagement/examples/portfolio_tool_bi.json

# Inline JSON
python3 .claude/skills/launch-engagement/scripts/validate_intake.py \
  --json '{"kind":"portfolio","name":"Demo","delivery_lane":"advisory-only"}'

# Stdin
cat examples/portfolio_tool_bi.json | python3 scripts/validate_intake.py --root ../..
```

Schema: `intake.schema.json` (reference/documentation — runtime enforcement is in
`intake_normalize.py`; `test_schema_enums_match_constants` guards drift).
Examples: `examples/`.

### State-file versioning

`.engagement_state.json` carries a `schema_version` (`engagement_constants.STATE_SCHEMA_VERSION`,
currently `1.0`). The producer stamps it; the consumer (`start-project` `build_project.load_state_file`)
refuses a state file whose **major** version it does not understand, so a breaking change to the state
contract fails loudly instead of being silently mis-read. Bump the MAJOR only on a breaking change; an
absent version (legacy files) is treated as compatible.

### Phase 0 definition of done

**Machine (validator / start-project):**

- Dossier (`<project_path>.md`)
- Project folder
- `SOP Runbook.md`
- `Engagement_Runbook.md`
- `Deliverables/00_Statement_of_Work.md`
- `Deliverables/00_Brand_and_Design_System.md`

**Human (orchestrator / owner):** fill SOW/brand/kickoff judgment content, append
daily log, and (still manual) CRM pipeline row / Portfolio Hub link per
`/start-project`.

## Module layout

| Module | Role |
|---|---|
| `validate_intake.py` | CLI entrypoint + `phase0_action` detection |
| `intake_normalize.py` | Field validation, defaults, path rules |
| `intake_readiness.py` | Resume artifact checks (kit-aware via manifest `deploy_root`) |
| `intake_commands.py` | Emits `start-project` / `project-kit` command arrays |
| `intake_schema.py` | `Intake` + `IntakeResult` dataclasses |
| `kit_registry.py` | Loads `06_Templates/Kits/*/manifest.json` |
| `_paths.py` | Vault-root import bootstrap |

Shared enums: `scripts/engagement_constants.py` (also used by `start-project`).

## Extending Phase 0

1. Add artifacts to `intake_readiness.readiness_requirements` (and the table below).
2. If the create/sync boundary changes, update `determine_phase0_action` in
   `validate_intake.py` and the DoD list above.
3. Keep `intake.schema.json` enums aligned with `engagement_constants` (test-enforced).
4. Mirror every edit into `.agents/skills/launch-engagement/`.

## Resume artifact matrix

| `starting_phase` | Required artifacts |
|---|---|
| 0 | None |
| 1 | Dossier (`.md`), project folder, `SOP Runbook.md`, `Engagement_Runbook.md`, `Deliverables/00_Statement_of_Work.md`, `Deliverables/00_Brand_and_Design_System.md` |
| 2 | + `Deliverables/01_Situation_Assessment.md` |
| 3 | + `Deliverables/02_KPI_Design.md` |
| 4 (tool-built-bi) | + `<kit deploy_root>/AI Build Runbook.md` |
| 5 (tool-built-bi) | + `<kit deploy_root>/Build Recipe (TEMPLATE).md` |

## Tests

```bash
python3 .claude/skills/launch-engagement/tests/test_validate_intake.py -v
```

Coverage includes a **downstream-command contract test** (parses the emitted
`start-project` `--state-file` command through the real `build_project.build_parser()`
and asserts state JSON fields the downstream loader needs), a **schema-drift guard**,
a **dual-tree sync guard** (`.claude` vs `.agents` skill copies), and an
**end-to-end integration test** (`test_end_to_end_phase0.py`) that seeds a temp vault
with the real templates, runs the emitted `build_project.py create --state-file`
command for real, asserts all six Phase-0 DoD artifacts exist without touching any
canonical SOP, and confirms a second intake run flips to `load_existing`. Lane
skip-phase sets live in `engagement_constants` (`SOFTWARE_CODE_SKIP_PHASES`,
`ADVISORY_ONLY_SKIP_PHASES`) — the resume guard and phase plan share them.
