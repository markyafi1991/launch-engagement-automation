# Intake — parameterize the engagement before anything runs

The pipeline refuses to start on loose prompt judgment. Every engagement begins as a
typed JSON intake that is validated, normalized, and persisted as machine state; the
validator then emits the exact commands every downstream phase will use.

## Field contract

Three fields are required, two are conditional on what the first three say, and the rest
take defaults. Unknown fields are rejected outright rather than ignored — a typo in a key
name fails the run instead of silently dropping the value.

| JSON field | Requirement | Default | Notes |
|---|---|---|---|
| `kind` | Required | — | `client` or `portfolio` |
| `name` | Required | — | Engagement / project name (no path separators, no `.`/`..`) |
| `delivery_lane` | Required | — | `tool-built-bi`, `software-code`, or `advisory-only` |
| `kit` | Conditional | — | Required when `delivery_lane` is `tool-built-bi`; must match a kit manifest name. Rejected on any other lane |
| `source` | Conditional | — | Required when `kind` is `client` (CRM acquisition source) |
| `industry` | Optional | `""` | Passed through to the scaffolder |
| `engagement_type` | Optional | `analytics` | `analytics`, `automation`, or `advisory` |
| `data_classification` | Optional | `internal` (client) / `synthetic` (portfolio) | Portfolio allows only `synthetic` or `public` |
| `deliverables` | Optional | `["Dashboard"]` | Array of short deliverable descriptions; blank entries are dropped |
| `project_path` | Optional | derived from kind + name | Must stay under the correct area |
| `starting_phase` | Optional | `0` | Resume point (0-9); validator checks prior-phase artifacts exist |
| `status` | Optional | `prospect` (client) / `active` (portfolio) | Client CRM status |
| `include_portfolio_readout` | Optional | `false` | When `true`, portfolio builds keep Phase 7 |
| `discovery` | Phase 1 required | `{}` | Decision context, reporting period, data gaps, stakeholders, and the `approved_sources` allowlist. Not accepted by the validator shipped here — see [Where this extract differs](#where-this-extract-differs) |

Path rules are enforced, not advisory: `project_path` is resolved against the repository
root and must stay inside it, must begin with `02_Clients` for a client or `04_Portfolio`
for a portfolio build, must name a project folder, and may not point into a confidential
client subfolder (`intake`, `contracts`, `client-comms`) or into `data/raw`.

The JSON schema (`intake.schema.json`) is the documented contract; runtime enforcement
lives in `intake_normalize.py`. Drift tests keep the two from silently diverging.

## Steps

1. Collect or confirm the required fields with the owner.
2. Run the validator:

   ```bash
   python3 .claude/skills/launch-engagement/scripts/validate_intake.py --file intake.json
   ```

   In the full system this is read-only; state is written only when `--write` is passed.
   The copy in this repository has no `--write` and always persists — see below.
3. Review the output: normalized values, applied defaults, hydration notes, readiness
   result, the resolved `phase0_action`, and the emitted per-phase command plan.
4. Persist state (`--write` in the full system). This creates an isolated, versioned,
   gitignored state file at `.engagement_states/<project-digest>.json` — the digest is the
   first 16 hex characters of the SHA-256 of the project path — plus an `index.json`
   mapping project paths to state files. Writes are atomic and revision-checked.
5. Use the emitted commands (`start_project_command`, `discovery_commands`,
   `kpi_commands`, `phase3_commands` ... `phase7_commands`) verbatim in later phases —
   they all reference the same engagement-specific state contract.

The state file is per engagement by design. One engagement must never be able to
overwrite another's state, which is why the shared constants module carries an explicit
prohibition on a singleton state filename.

## Phase 0 routing

The validator resolves one of three actions and emits the matching command. Nothing about
this is inferred at run time by an agent.

| `phase0_action` | Meaning | Emitted `start_project_command` |
|---|---|---|
| `create` | No dossier, folder, or SOP runbook exists yet | `build_project.py create --state-file <state>` |
| `sync_existing` | A scaffold exists but is incomplete, empty, or still raw template | `build_project.py sync --state-file <state>` |
| `load_existing` | Machine artifacts are present and pass the content floor | Empty — nothing to run |

`load_existing` is a statement about the machine scaffold only. It does not mean the
engagement is client-ready; the human documents it leaves behind are tracked separately
(see [02_phase_0_scaffold.md](02_phase_0_scaffold.md)).

## Protections built into the validator

- **Dossier hydration** — when the project dossier already exists, its frontmatter
  overrides matching intake values (the persisted dossier is canonical for an existing
  project). The hydrated keys are `project-kind`, `delivery-lane`, `industry`,
  `engagement-type`, `data-classification`, `deliverables`, `source`, and `status`.
  **Consequence:** editing the dossier is how you change a hydrated field on an existing
  engagement. Passing a new value in the intake JSON alone is overridden. Every override
  is surfaced as a hydration note on stdout, so re-parameterization conflicts are always
  visible rather than silent.
- **Approved-discovery clobber guard** — a state write refuses to overwrite an approved
  discovery intake with a payload whose hash differs from the approval.
- **Resume readiness** — `starting_phase > 0` requires the full prior-phase artifact
  matrix to exist and every prior gate to still verify (see
  [12_cross_cutting.md](12_cross_cutting.md)).
- **Partial-scaffold guard** — on `starting_phase: 0`, a project whose base scaffold
  exists only in part fails closed rather than letting `create` overwrite or split state.
- **Phase 0 content floor** — existing scaffold artifacts must be non-empty and free of
  unreplaced `{{placeholder}}` tokens to count as "existing"; raw template copies route
  to a heal/sync action instead. `TBD` stubs pass the machine floor.
- **Lane filtering** — the emitted `phases` array is the lane-filtered execution plan
  (kit phases only for `tool-built-bi`, and so on). Portfolio builds drop Phase 7 unless
  `include_portfolio_readout` is `true`. A `software-code` engagement cannot resume into
  a kit phase at all; the validator rejects the payload rather than emitting a plan that
  skips the phase it was asked to start at.

## Where this extract differs

This repository is a sanitized extract, and the intake pipeline is one of the two things
in it that actually runs. The code here is an earlier generation than the private tree the
sections above describe. These are known limitations, stated plainly rather than papered
over — everything below was verified by running the shipped code.

- **A single shared state file.** The shipped validator writes `.engagement_state.json` at
  the repository root, `schema_version` `"1.0"` — one file, reused by every engagement. The
  private tree replaced this with the per-engagement
  `.engagement_states/<digest>.json` plus `index.json` at schema version 2, precisely
  because a singleton lets one engagement overwrite another. Running two engagements
  against one checkout here will do exactly that: the second validate silently replaces the
  first engagement's state, and the Phase 0 command that reads it will then scaffold
  against the wrong project. Work one engagement per checkout, or move the state file aside
  between runs.
- **No `--write`; persistence is unconditional.** The shipped CLI accepts only `--root`,
  `--file`, and `--json`. Every successful run writes state; a failed write degrades to a
  warning on stderr rather than a non-zero exit. The read-only-by-default contract is
  private-tree behavior.
- **No `discovery` field.** The shipped intake surface is the 13 fields above minus
  `discovery`; passing it fails with `Unsupported intake field(s): discovery`. The Phase 1
  runner that consumes discovery seed data is not part of this extract, so there is nothing
  here to feed.
- **No dossier hydration.** The hydration module is not included. An existing dossier's
  frontmatter does not override intake values in this copy.
- **Existence checks, not the content floor.** `phase0_action` is resolved by testing
  whether paths exist. An empty file or an unreplaced `{{placeholder}}` copy counts as
  present here, so a hollow scaffold routes to `load_existing` instead of `sync_existing`.
- **Fewer emitted commands.** Output carries `phase0_action`, `start_project_command`,
  `kit_deploy_dry_run_command`, `phases`, `dossier_path`, `work_surface`, `state_path`, and
  `schema_version`. The per-phase command sets belong to the gate runners that are not
  shipped. `state_path` is emitted as an absolute path resolved from `--root`.
- **Resume checks are existence-only, through Phase 5.** No gate recomputation, hash
  binding, or approval expiry — those read gate files produced by the unshipped runners.
- **`advisory-only` keeps Phase 6 in the plan.** The shipped skip set for that lane is
  phases 3-5; the private tree skips 3-6.

## Human vs agent

Agent: everything in this phase. The intake is machine work end to end; the owner only
supplies or confirms the field values.
