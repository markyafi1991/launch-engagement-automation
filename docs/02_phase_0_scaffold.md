# Phase 0 — Scaffold (start-project)

Creates the engagement's home: the project dossier, working folders, engagement runbook,
Phase 0 deliverable stubs, and a project-specific SOP runbook generated from the
canonical procedure library — without ever modifying the canonical SOPs themselves.

Engine: the `start-project` skill (`build_project.py`), invoked with the validator's
emitted `start_project_command` and the engagement `--state-file`.

## Preconditions

- Validated intake state exists (`.engagement_states/<digest>.json`).
- Guardrails: never overwrite an existing dossier with `create`; portfolio data
  classification must be `synthetic` or `public`; real client data never lands in the
  portfolio area.

## Steps

1. **Route.** The validator's `phase0_action` decides:
   - `create` — no project exists; scaffold from scratch.
   - `sync_existing` — artifacts exist but are empty or raw-template; heal them.
   - `load_existing` — artifacts pass the content floor; load and confirm metadata.
2. **Preview.** Run the create command with `--dry-run` first; review the printed paths
   and applicability decisions.
3. **Execute.** Rerun without `--dry-run`. The scaffolder creates:
   - the project dossier (frontmatter records kind, lane, classification, status),
   - standard working folders,
   - `Engagement_Runbook.md` hydrated from the engagement template (every
     `{{placeholder}}` filled or swept to `TBD`),
   - `Deliverables/00_Statement_of_Work.md` and
     `Deliverables/00_Brand_and_Design_System.md`,
   - clients additionally: `Deliverables/00_Kickoff_Charter.md` plus the client folder
     README and the onboarding and offboarding checklists,
   - `Deliverables/01_Situation_Assessment (TEMPLATE).md` starter for Phase 1 — kept as a
     visibly named template so a resume check can never mistake an untouched starter for
     completed Discovery output,
   - `SOP Runbook.md` — the applicable canonical SOP links, known gaps, and an
     improvement-capture checklist,
   - sensitive classifications (`confidential`, `financial`, `phi`): a `data/README.md`
     guardrail instead of a local raw-data landing zone.
4. **Inspect.** Open the dossier and runbook; add judgment-driven business context only
   after the deterministic scaffold is correct.
5. **Register (manual by design).** Client: add the CRM pipeline row. Portfolio: link
   the build into the portfolio hub (manually curated). Both: append the work to the
   daily operations log.
6. **Resync later if metadata changes:** `build_project.py sync --dossier <path>`
   regenerates the SOP runbook and backfills empty or raw-template engagement files;
   filled files are left alone.

## What each kind gets

The two kinds share a spine and diverge on the client paperwork and on the folder layout.

| | Portfolio | Client |
|---|---|---|
| Dossier | Portfolio dossier | Client dossier rendered from the client dossier template |
| Working folders | `project-plans`, `data/raw`, `models`, `docs`, `reports`, `exports` | `intake`, `contracts`, `client-comms`, `models`, `docs`, `reports`, `exports`, plus `data/raw` — or a guarded `data/` with a handling README when the classification is sensitive |
| `SOP Runbook.md` | Yes | Yes, with the client onboarding and data-access procedures included |
| `Engagement_Runbook.md` | Yes | Yes |
| `Deliverables/00_*` stubs | Statement of work and brand and design system are written, but are not gated | The three gated stubs: statement of work, brand and design system, kickoff charter |
| Client folder templates | — | Folder README, onboarding checklist, offboarding checklist |

The three client `Deliverables/00_*` stubs are what a client `load_existing` and any
client resume into Phase 1 require. A portfolio engagement is machine-complete on the
dossier, folder, `SOP Runbook.md`, and `Engagement_Runbook.md` alone.

## Registration stays manual

Neither the CRM pipeline row nor the portfolio hub link is written by the scaffolder. The
clients hub surfaces dossiers by query, so a client appears there as soon as its dossier
exists, but the pipeline row is a human edit. The portfolio hub is a curated list and is
meant to stay curated — a portfolio project earns its entry, it does not get one
automatically. Both, plus the daily operations log entry, are owner steps after the
scaffold is inspected.

## Human fill that remains after the machine scaffold

`load_existing` only means the machine scaffold is present. For clients, the SOW, brand
and design-system determination, and kickoff charter are human-completed documents
(kickoff judgment follows the kickoff SOP) before the engagement is client-ready. The
scaffolder writes those files with every placeholder resolved to `TBD`, which is exactly
what lets them pass the machine floor while still being empty of judgment — the machine
floor proves the file is real, not that it is finished.

## Gate

Phase 0 artifacts must be non-empty and free of unreplaced `{{placeholder}}` tokens (the
content floor). `TBD` stubs pass the machine floor — human fill is tracked separately.

## Where this extract differs

Phase 0 is the second of the two things in this repository that actually runs, so the
gaps in the shipped copy matter. Stated plainly:

- **The templates are not included.** `build_project.py` reads its engagement templates
  and, for clients, the client folder templates from the private vault tree and raises if
  they are missing. The `create` path therefore cannot run against a bare checkout — the
  Phase 0 end-to-end tests skip for exactly this reason. Supply equivalent templates at the
  expected paths to exercise it.
- **No kickoff charter.** The shipped template map has no client-only entry, so
  `Deliverables/00_Kickoff_Charter.md` is never scaffolded here.
- **Client and portfolio are not distinguished by the routing and readiness checks.** The
  shipped checks require the engagement runbook, the statement of work, and the brand
  stub for both kinds. A portfolio project is therefore held to two client documents it
  does not need, and a client project is not held to the kickoff charter it does.
- **`sync` backfills missing files only.** It does not heal empty or raw-template files;
  the private tree treats those as needing a rewrite, which is what makes
  `sync_existing` terminate instead of looping.
- **Placeholders are substituted, not swept.** The shipped hydration replaces a fixed list
  of known tokens. Any `{{placeholder}}` outside that list survives into the output
  instead of being swept to `TBD`.
- **The registration call is a dead stub.** `create` attempts a CRM and portfolio-hub
  registration whose implementation is not present and catches the resulting error, so
  every run prints a warning that automated registration was skipped. The behavior is
  correct — registration is manual — but the warning is noise, not a fault in your setup.

## Human vs agent

- Agent: routing, dry-run, scaffold, sync/heal, drafting the close-out report.
- Human: reviewing the dry-run before live run, SOW/brand/kickoff fill, manual registry
  entries, approving any SOP improvements the runbook proposes.
