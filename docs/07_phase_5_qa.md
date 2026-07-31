# Phase 5 — QA

Proves the build is right before anything ships: model QA, report QA, DAX regression
tests with expected-equals-actual results, performance and security evidence, all bound
into an immutable definition of done.

Engine: the Phase 5 QA runner, using the validator's emitted `phase5_commands`. Phase 5
starts from the valid Phase 4 build-candidate gate but owns the final post-QA artifact
inventory — legitimate QA fixes do not require a false Phase 4 re-approval, while
inventory-independent Phase 4 controls (validation-output pass language, repository
attestations, the human checkpoint) still carry forward.

## Steps

1. **Prepare.** `phase5_commands.prepare` revalidates Phase 4, captures its gate hash,
   creates the immutable `QA/phase5.dod.json` (freezing the required checklist item
   text from the kit templates and the report-load ceiling from the kit manifest), and
   copies the two deployed kit checklists into mutable project results:
   `QA/Model_Build_QA_Result.md` and `QA/Report_QA_Result.md`. Never tick or sign the
   deployed template files themselves. Stuck mid-flight: `prepare_force` resets Phase 5
   outputs after preflighting that the kit checklists and QA policy are intact.
2. **Complete the model QA checklist** (structure of the kit checklist):
   - Star-schema structure: isolated fact, single-direction one-to-many relationships,
     no ambiguous paths, Calendar marked as the one date table and spanning the full
     fact range.
   - Keys and grain: unique dimension keys, no null fact foreign keys, stated grain
     honored, row counts reconciled to source.
   - Measures: all in the measures table, safe division everywhere, format strings and
     display folders set, a known-good total pinned against a validated source figure,
     ratios in sane ranges, time intelligence graceful on partial periods.
   - Hygiene: helper/sort columns hidden, sort-by set, data types correct, auto
     date/time off.
   Items are completed without deleting, renaming, or replacing them: `[x]` for pass,
   or `[~]` plus a substantive `N/A:` rationale (minimum length enforced, boilerplate
   banned). No unchecked items or blank sign-off lines pass.
3. **Write and run DAX Query View tests.** Author assertions from the kit's test
   starter (null checks, distinct keys, ranges, known totals) as saved `.dax` files in
   the PBIP; run them against the open model. Produce structured DAX-results JSON:
   non-zero, unique, all-passed tests where each test's `expected` equals `actual`;
   every test ID matches a saved `.dax` filename; each source test cites its KPI IDs;
   all approved KPI IDs are covered.
4. **Complete the report QA checklist** (structure of the kit checklist):
   - Brand and layout: theme applied, layout matches the locked design, correct landing
     page, one headline answer per page.
   - Readability: correct number formats, titles that state the takeaway, favorability
     never color-only, useful tooltips, empty-selection state handled.
   - Accessibility and performance: alt text and tab order, WCAG AA contrast, page load
     within the frozen ceiling, custom visuals render in the service, not just Desktop.
   - Correctness: headline numbers match validated model-test totals, slicer and
     cross-filter behavior intentional, drill-throughs land, no leftover dev filters.
   Then open the final report in Desktop, test every authored page, reconcile numbers
   and interactions, record the Desktop version and the maximum page load, and save
   structured report-evidence JSON plus project-local evidence notes.
5. **Record structured security evidence:** workspace permissions, external sharing,
   refresh identity, and row-level security. Client and sensitive builds require all
   four checks to pass — a passed RLS check requires roles plus a negative-authorization
   test. Portfolio N/A entries need substantive rationales. A check may honestly record
   `failed` mid-review, which blocks the gate until resolved. The runner also scans the
   PBIP and all QA text for secret assignments, private keys, bearer tokens, local user
   paths, and (for sensitive classifications) SSN or payment-card-like literals, and
   re-runs the repository safeguards and Phase 4 carry-forward controls.
6. **Commit the gate.** `phase5_commands.commit_gate` (interactive owner terminal for
   the approval prompt) passes the structured DAX, report, and security evidence — or
   use the split `evidence` / `approve` / `validate` commands when debugging.
   `scaffold_evidence` writes empty JSON templates to fill; scaffolding never
   fabricates a pass. The final gate binds every source hash, writes
   `phase5.gate.json`, and marks Phase 6 ready. `check` gives read-only resume
   diagnostics.

## Trust boundary

The machine verifies file shape, hashes, checklist-item binding, expected-equals-actual
on DAX results, text scans, and git safeguards. It does not open Power BI Desktop, run
DAX Query View, or query live workspace permissions — those remain owner attestation in
the structured evidence files.

## Human vs agent

- Agent: prepare, checklist drafting, test authoring, evidence assembly, scans, gate
  runs.
- Human: the Desktop click-through, the actual test executions it attests, security
  review judgments, sign-offs, and the gate approval.
