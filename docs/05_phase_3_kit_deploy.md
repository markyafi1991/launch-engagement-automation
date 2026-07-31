# Phase 3 — Kit deploy + work surface (project-kit)

Deploys the reusable delivery kit (the technical build payload) into the project and
provisions the execution tracker. Only runs when `delivery_lane` is `tool-built-bi`;
software builds route to the engineering tracker instead, and advisory engagements skip
kit phases entirely.

Engine: the `project-kit` skill plus the ClickUp provisioner, using the validator's
emitted `phase3_commands`.

## What a kit is

A kit is a packaged, tool-specific bundle of build accelerators kept canonical in a
templates library and copied out per project — never edited in place. The Power BI
Project Kit (v1.2) deploys to `<project>/Power BI Kit/` and carries:

- `AI Build Runbook.md` — the Phase 4 build sequence (report-as-code)
- `Build Recipe (TEMPLATE).md` — the reproducible per-build record
- `Assets/` — brand theme JSON, PBIP structure reference, DAX starter library,
  DAX Query View test starter, synthetic data generator, report layout mockup (HTML),
  TMDL model starters (Calendar, measures table), Deneb custom-visual template,
  a PBIP-scoped gitignore
- `Checklists/` — Model Build QA checklist, Report Polish and Handoff checklist
- `Deliverable Templates/` — Dashboard Requirements, Measure Dictionary
- `Scripts/` — the PBIP validator used by the Phase 4 gate
- `Diagram.mmd` — the kit's architecture diagram (Mermaid source of truth)

A kit deploy is an instantiation: the kit is the class, each deployed project the
object.

## Steps

1. **Dry run.** `phase3_commands.deploy_dry_run` — the deploy script validates the
   complete manifest and all source/destination containment before its first write.
   Confirm, then run `phase3_commands.deploy` live. Deploys never overwrite existing
   files.
2. **Hydrate requirements.** `phase3_commands.hydrate` mechanically transcribes the
   approved Phase 2 `KPI-NNN` IDs into the deployed `Dashboard_Requirements` document,
   binds against the approved KPI hash, and sweeps leftover `{{...}}` tokens to `TBD`.
   Human judgment then replaces the TBD sections (audience and how-used, pages and
   layout, data, sign-off) before build. The requirements document is the build
   contract: audience, decisions served, KPI table, pages and layout (with the agreed
   mockup attached), data grain and refresh, non-functional needs (brand, distribution,
   row-level security, performance target), out-of-scope, and sign-off.
3. **Fill the Build Recipe** completely — the build plan section (intended order, PBIP
   path, validation tool, Desktop version target, data boundary, baseline commit,
   expected human checkpoint) must contain no `{{...}}`, `TBD`, or `TODO` before the
   gate.
4. **Provision the tracker.** `phase3_commands.provision_clickup` instantiates the
   ClickUp list template inside the portfolio delivery space (requires an API token and
   a configured template id — empty fails closed). The milestone-driven structure:
   one list per project; stages live as milestone gate-tasks inside the list, each
   milestone carrying an owner assignee and a written definition of done; tasks and
   subtasks under each stage; estimates at the leaf level; progression gated by
   milestone-to-milestone `waiting_on` dependencies rather than calendar dates. The
   provisioner is idempotent on an existing live list, writes
   `<project>/clickup_receipt.json`, and POSTs the dependency chain.
5. **Stamp IDs back.** Record the list and milestone IDs in the project dossier and
   project index — the vault note and the tracker item reference each other.
6. **Gate.** First run: `phase3_commands.gate_with_rollback`; re-runs and resumes:
   `phase3_commands.gate`. Phase 4 stays blocked until `phase3.gate.json` verifies:
   - template fidelity for non-planning kit files (deployed copies match the canonical
     kit, id-stamp-normalized),
   - a filled Build Recipe (strict — no placeholders),
   - hydrated Requirements (all KPI IDs present, no mustache; TBD allowed at this gate),
   - a receipt with `dependencies_applied: true`.

   Rollback (first-run only, opt-in) moves the deployed kit directory to a timestamped
   recoverable sibling — nothing is deleted locally, so a human-filled Build Recipe
   survives — and deletes the tracker list (recoverable from its trash).

## Trust boundary

The provision step POSTs dependencies to the live tracker, but the downstream gate
verifies the local receipt only (offline — it does not re-query the tracker), so
`dependencies_applied` attests to the provision run, not to current live tracker state.
Resume re-reads the on-disk receipt; a re-provisioned or edited receipt invalidates the
gate.

## Human vs agent

- Agent: dry-run, deploy, hydrate, tracker provisioning, gate runs.
- Human: confirming the dry-run, judgment fill of the requirements TBD sections and the
  Build Recipe plan, choosing the kit and target when ambiguous.
