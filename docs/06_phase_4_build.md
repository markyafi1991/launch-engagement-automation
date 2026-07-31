# Phase 4 — Build (report as code)

The build itself: a Power BI deliverable authored as much by AI as possible. This works
because a PBIP project is plain text — the semantic model is TMDL and every visual is a
PBIR JSON file — so the agent can write the model and report directly, and the Power BI
Modeling MCP server can edit the model programmatically.

Engine: the deployed AI Build Runbook, wrapped by the validator's emitted
`phase4_commands` (prepare, evidence, validate).

## Honest automation map

| Fully AI-authorable | AI-authorable with a human apply/refresh step | Human-in-the-loop |
|---|---|---|
| TMDL model text (tables, measures, relationships) | Applying TMDL/PBIR changes into an open Desktop (restart/refresh to reload) | Enabling preview features and MCP tenant toggle (one-time) |
| PBIR page/visual JSON | Data refresh and credential entry | Final visual-polish judgment, client sign-off |
| DAX measures and DAX Query View tests | Running the PowerShell test harness | Anything touching real client data classification |
| Deneb (Vega-Lite) and HTML-Viewer specs | Publishing / deploy | |
| Theme, synthetic data, docs | | |

Known seams, recorded rather than hidden: the Modeling MCP edits the model but not
report pages; the Skills-for-Fabric authoring chain cannot yet write KPI-card reference
labels (undocumented visual internals — use the Deneb route for variance KPI cards);
editor TMDL/PBIR edits are not reflected live in an open Desktop (restart to reload).
Plan the build around these seams; never claim a fully hands-off pipeline.

## Prerequisites and security preflight

1. Power BI Desktop with the PBIR enhanced-metadata preview feature enabled; record the
   exact Desktop version in the evidence file.
2. An editor with TMDL language support.
3. Optional: the local Power BI Modeling MCP server for model authoring (distinct from
   the remote query MCP; runs under the operator's identity — review enabled tools and
   apply least privilege before connecting client data).
4. Git, with a private repository for client work and a clean baseline commit before any
   AI edits.
5. Client raw data and credentials stay outside the repository; the kit's PBIP
   gitignore is copied to the project root as defense in depth, not the primary control.

## Orchestration wrapper

1. Commit the approved Phase 3 state, then run `phase4_commands.prepare` — it re-checks
   the Phase 3 gate, captures the current git HEAD as the rollback baseline, and marks
   Phase 4 in progress (warning on any uncommitted project paths, which a rollback could
   not restore).
2. Execute Build Steps 0-4 below. Do not push or publish in Phase 4 — those belong to
   the outer QA and handoff gates.
3. Record actual work, dated, under the Build Recipe's execution log: commands run,
   outputs, deviations, validation results, evidence paths.

## Build Step 0 — Frame (the design contract)

- Complete `Dashboard_Requirements`: audience, decisions driven, the approved KPI
  table, grain, refresh, sources, brand.
- Lock the visual contract before any build, at one of two fidelity levels:
  - **High-fidelity (design-first): dashboard design in Figma.** After KPIs are decided
    and before any visual build: create the frame at report aspect ratio (driven
    through the Figma MCP), lay out the visual hierarchy (what the reader sees first,
    one primary message per zone), apply the design system (brand tokens, type scale,
    spacing grid, favorability colors with a non-color cue for accessibility), mock
    every non-native visual (variance cards, benchmarking table, bullet charts) so the
    build target is unambiguous, then export the spec — screenshot/redline plus the
    token and spacing values — into the project. Definition of done: a high-fi frame at
    the real aspect ratio, on the house palette, grid-aligned; every planned visual
    mocked; a spec the build can follow without guessing.
  - **Low-fidelity fallback:** customize the kit's HTML layout mockup and screenshot it
    into the requirements.
- Either way, the build executes a decided layout instead of being art-directed live in
  Power BI.

## Build Step 1 — Data

- Portfolio/demo: run the kit's synthetic data generator (it writes a parameter/hash
  manifest and refuses overwrite without `--force`). Portfolio classification must be
  synthetic or public.
- Real client: raw files and credentials stay outside the repository; a cache-file
  exclusion alone is not a client-data boundary.

## Build Step 2 — Scaffold the PBIP

- Create the project via Desktop "Save As > Power BI Project (.pbip)" or by writing the
  folder tree from the kit's PBIP structure reference (`<Project>.pbip`,
  `<Project>.Report/`, `<Project>.SemanticModel/`, `.gitignore`).
- Copy the brand theme JSON into the report's registered resources and reference it.
- Copy the kit's PBIP gitignore to the project root.

## Build Step 3 — Model (TMDL, AI-authored)

Procedure follows the star-schema SOP:

1. Import fact and dimension tables separately — never pre-joined flat.
2. Set data types in Power Query (dates as Date, amounts as numeric).
3. Relate dimensions to the fact: one-to-many, single direction, on key columns; no
   bidirectional filters without a proven need.
4. Seed the Calendar table and mark it as the date table (the non-negotiable step for
   time intelligence).
5. Author measures into a dedicated measures table — never implicit column
   aggregations. Start from the kit's DAX starter library (placeholders renamed to real
   tables/columns), grouped with display folders, each with a format string. Author
   directly in TMDL or through the Modeling MCP (connect to the open model, then add
   measures/columns/relationships programmatically).
6. Validate one slice against a hand calculation before building anything downstream.

## Build Step 4 — Report (PBIR, AI-authored)

Build pages and visuals to the locked design spec. Authoring routes:

- **Skills-for-Fabric chain** (if installed): the report planner / report designer /
  report authoring skills write visuals into the PBIP, self-validating with
  desktop-bridge screenshots. Modeling still runs over the MCP.
- **Direct PBIR:** write `pages/<Page>/visuals/<id>/visual.json` per the structure
  reference. Fastest reliable path when a visual's JSON shape is uncertain: build one
  by hand in Desktop, save, read the generated JSON, then replicate.
- **Non-native visuals** (bullet charts, variance KPI cards, benchmarking dots): ground
  the agent in the model's actual TMDL files (so it writes against real table and
  column names), then generate one visual at a time as a Deneb Vega-Lite spec or an
  HTML-Viewer DAX measure; bind, render, verify favorability logic; a blank visual is
  almost always a field-name mismatch.
- Apply the theme; verify palette and typography against the design spec.

Then close the step:

1. Run the kit's PBIP validator and save its output inside the project. The evidence
   runner parses that output — failure language always fails, even alongside pass
   language; it never invents a pass.
2. Generate `phase4.evidence.json` via `phase4_commands.evidence`, passing the Desktop
   version and validator output path. Evidence requires a currently valid PBIP build
   and records the artifact-inventory SHA-256 — any TMDL/PBIR edit afterwards
   invalidates it. Repository-privacy and raw-data attestations are explicit CLI flags
   (required for sensitive classifications, which also require a live git remote
   recorded in evidence); hand-written evidence files fail closed.
3. Owner reviews the entire build locally and records the `human_validation`
   checkpoint — an interactive owner secret plus a project-local evidence note that
   cites the SHA-256 of `phase4.evidence.json`.
4. Run `phase4_commands.validate`. It fails closed unless the PBIP tree is non-hollow
   (at least one measure, populated page/visual JSON), the Build Recipe execution log is
   non-stub, validation output still reads as a pass, gitignore safeguards are active,
   tracked and untracked secret/data files are clean, and the human checkpoint is
   bound. Success writes `phase4.gate.json` and marks Phase 5 ready.

## Verification layer

Run the `verify-build` discipline as the human-readable stress-test and reporting layer
(definition of done pinned first, verify-as-you-build loop, stress test, report
"verified, not just asserted" with evidence); the machine gate is the durable
enforcement layer underneath it.

## Human vs agent

- Agent: synthetic data, PBIP scaffold, TMDL, DAX, tests, PBIR visuals, Deneb/HTML
  specs, theme, validator and evidence runs.
- Human: Desktop clicks (preview features, save/refresh/reopen), design judgment on the
  locked spec, the recorded review checkpoint, and explicit confirmation before the
  phase advances.
