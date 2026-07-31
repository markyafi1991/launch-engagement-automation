# Cross-cutting controls

Controls that run through every phase rather than belonging to one.

## verify-build — the verification discipline

Invoked before any phase reports "done." The method:

1. **Write the definition of done first.** Objective, checkable criteria pinned before
   building (for a report: every page screenshotted, no errors, numbers reconcile; for
   a pipeline: runs end to end, counts and schema match, records spot-checked; for an
   automation: the effect verified at the destination, never from the agent's own
   say-so).
2. **Verify as you build.** Iterate in a loop — run it, look at it, fix it — capturing
   evidence (screenshots, counts, log excerpts) as you go, aiming to be ~90% correct
   before the owner reviews once.
3. **Stress test the finished thing.** Attack it: malformed inputs, boundary values,
   empty and huge inputs, duplicate submissions, permission edges. Report the tally and
   honest non-blocking notes on residual risks even when everything passes.
4. **Report with evidence** — "verified, not just asserted": what was checked, the
   evidence, what is confirmed working, and the residual risks. Where possible the
   verification pass runs in a separate context from the build (worker and judge are
   not the same).

In this pipeline, verify-build is the human-readable reporting layer; the per-phase
machine gates are the durable enforcement layer.

## The citation gate — provenance or it doesn't ship

Every substantive factual claim, statistic, quotation, framework, or borrowed phrasing
in an external deliverable must trace to a specific source. The pre-ship check:

1. Extract every substantive claim from the target (the author's own analysis is
   exempt).
2. Map each claim to a source — a stored source note's citation handle, or a named
   external reference — marking each Traceable, Needs-source, or Verbatim-risk.
3. Build the References section with inline markers.
4. Plagiarism pass: any passage reproducing a source's wording without quotation marks
   must become a quoted, cited excerpt or be rewritten.
5. Verdict: **SHIP** (every claim traceable — "N claims, N cited, 0 untraceable") or
   **BLOCKED** (each unresolved claim listed; for external deliverables a hard stop
   until each is sourced, quoted, or cut).

Phase 6 encodes the machine half of this gate as `citation-receipt.json` (per-claim
rows, hash-bound to the shipped artifacts); the substantive check of each claim is the
human half. A companion audit mode sweeps the ingest side — confirming stored sources
remain referenceable — so generation always has something real to cite.

## State machine and debugging

- All engagement state lives in `.engagement_states/<project-digest>.json`
  (gitignored, atomic, revision-checked) with an `index.json` map; the project dossier
  frontmatter is the human-readable projection.
- A debug command prints the lane-filtered phase plan, the Phase 0 routing decision,
  every approval-gate status, and any dossier-versus-state metadata drift.

## Resume rules

`starting_phase` in the intake resumes a partial engagement, but only when the full
prior-phase artifact matrix still verifies:

| Resuming at | Requires |
|---|---|
| Phase 1 | Dossier, project folder, SOP runbook, engagement runbook; clients also SOW, brand and design system, kickoff charter |
| Phase 2 | Owner-approved Situation Assessment, semantic hash unchanged, approval at most 14 days old |
| Phase 3 | Owner-approved KPI design, semantic hash and approved-discovery hash unchanged |
| Phase 4 | Deployed kit runbook present |
| Phase 5 | Recomputed, verified Phase 4 gate (artifacts, recipe, validation output, checkpoint evidence all unchanged) |
| Phase 6 | Recomputed, verified Phase 5 gate (final inventory, evidence, checklists, DoD, approval) |
| Phase 7+ | Recomputed, verified Phase 6 handoff gate (package, coverage, receipts, scan, approval) |
| Phase 8+ | Recomputed Phase 7 gate for clients and opted-in portfolio readouts |

Lane boundaries: software-code engagements cannot resume into kit phases 3-6;
advisory-only plans skip them; portfolio engagements that skipped the readout do not
fabricate that prerequisite.

## Trust boundaries, stated honestly

A design theme across every gate:

- The machine verifies structure, hashes, freshness, coverage, text scans, and recorded
  attestations. It does not open desktop applications, run interactive tools, or query
  live external systems — those remain explicit human attestation, recorded in
  evidence files the gates hash-bind.
- The interactive owner-secret prompt at every approval is a deterrent and audit
  trail, not authentication: a persisted approval records that whoever held the secret
  and a terminal signed off, not cryptographic proof of which human.
- Fail-closed is the default everywhere: missing evidence, placeholders, hollow
  artifacts, stale hashes, or drift block the phase rather than degrade it.

## Structural authorization ("keys, not prompts")

Permissions are scoped structurally, not by instruction: the reconcile engine has no
network access; deploy scripts validate containment before writing; sensitive
classifications force explicit CLI attestations; state files are gitignored and
owner-readable; canonical templates are copied out, never edited in place. Rules that
matter are enforced by the shape of the system, not by asking an agent to behave.
