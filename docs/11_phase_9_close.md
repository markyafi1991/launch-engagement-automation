# Phase 9 — Close

Ends the engagement cleanly and feeds what was learned back into the system, so the
next engagement starts better than this one did. Every closeout fact — acceptance,
payment, handoff, archive, work-surface state — has to be affirmed deliberately and
backed by its own evidence file; nothing about a close is assumed.

Engines: the Phase 9 close runner, using the validator's emitted `phase9_commands`, and
wrapping the closeout and retrospective procedure, the `daily-log` skill, and the
`task-reconcile` skill. Phase 9 is a stateful cross-lane terminal gate and always starts
from the recomputed verified Phase 8 gate.

## Closeout steps

1. **Prepare.** `phase9_commands.prepare` writes the immutable
   `Deliverables/Closeout/phase9.dod.json` (hash-bound in state, as in Phase 8), the
   canonical `Closeout_Report.md` and `Retrospective.md` drafts, and a
   `closeout_attestation.json` in which **every status is `pending`**. The scaffold never
   pre-asserts `accepted`, `paid`, or `closed`, so affirming a closeout fact is always a
   deliberate edit and an unedited scaffold fails closed. `prepare_force` moves prior
   output and gate into a recoverable `Closeout.rolledback-<UTC>` directory and restores
   the prior dossier and state status — fail closed, because the dossier is parsed
   *before* anything is moved, so an unparseable dossier leaves the tree untouched
   rather than half-reset. The frozen definition-of-done requirement IDs are enforced
   against the attestation; editing them after prepare fails closed.
2. **Confirm acceptance** against the statement of work's acceptance criteria. Client
   engagements require acceptance evidence — the record a dispute would turn on.
   Portfolio engagements use owner acceptance instead.
3. **Final invoice and collect.** Clients record a sanitized paid-invoice pointer (at
   least 8 characters, not a placeholder) — a pointer only; invoice contents never enter
   the attestation. Portfolio engagements use `not_applicable` financial status.
4. **Verify the handoff** — access transferred, documentation delivered, the "how to
   read it" guide in the client's hands — and record verified handoff evidence.
5. **Ask for a testimonial and referral** while the value is fresh, and record the
   `request_reference` (at least 8 characters, not a placeholder). Portfolio uses
   `not_applicable`.
6. **Archive** the engagement folder and update the operating records per the write
   protocol. Every engagement — client or portfolio — needs an archive disposition
   **with a project-local evidence file**: an archive manifest when the disposition is
   `archived`, a retention decision note when it is `retained-active`.
7. **Retrospective** — what worked, what caused friction, and what to fix in the system.
   The fix lands in the owning procedure or skill, not just in memory: the attestation
   records a substantive retro plus a system-improvement path or work-item ID.
8. **Reconcile the work surface** and drive it to a terminal `closed` state — ClickUp
   for the BI and advisory lanes, Linear for software-code — recording a real
   `external_id` and a timezone-aware `reconciled_at`.
9. **Commit the gate.** `phase9_commands.commit_gate --approved-by <owner>` from an
   interactive owner terminal, or the split `evidence` / `approve` / `validate` commands
   when debugging. Success writes `phase9.gate.json` — including
   `work_surface_verification.mode`, one of `live_clickup`, `attestation_only`, or
   `check_failed` — marks Phase 9 complete, sets `engagement_status: closed`, and sets
   the client record to `closed`.
10. **To correct or re-approve an already-gated close, reopen — do not force-prepare.**
    `reopen` keeps the artifacts and the frozen definition of done and reverses all
    three terminal markers (engagement status, client status, dossier frontmatter), so
    nothing advertises a closed engagement while it is open for re-approval.

## Evidence rules

- **Evidence stays inside the project directory.** Symlinks and path escape are
  rejected.
- **Every evidence file must be substantive** — at least 40 non-whitespace characters,
  and at least 120 for client acceptance, which is the record a dispute would turn on.
- **Each attested fact needs its own file.** Aliasing one note as acceptance evidence
  *and* handoff evidence *and* archive evidence is rejected outright.
- **Scans cover the evidence, not just the paperwork.** Unresolved whole-word `TBD` and
  `TODO` markers, secrets, local user paths, and sensitive-number literals are rejected
  in the acceptance, handoff, archive, and case-study evidence files as well as in the
  closeout report, retrospective, and attestation JSON.

## Operations log (daily-log)

Every substantive session in the engagement — and the close itself — is recorded in the
daily operations log with five ledgers, append-only:

1. Resolve or create today's log note from the template.
2. Append one row per ledger as applicable:
   - **Work session** — time, trigger, workstream, outcome, status.
   - **Change** — one row per logical change: area, files touched, change type, why,
     verification. Bulk edits may cite a directory prefix.
   - **Verification** — check, command or method, result, follow-up.
   - **External actions and boundaries** — anything that left the system.
   - **Risks / open questions.**
3. Run the log-compliance self-check; every committed path must be covered by a Change
   row before the pre-commit gate passes.

## Tracker reconcile (task-reconcile)

Reflects work-surface state built directly in the tracker back into the knowledge base
as read-only reference notes — the tracker stays canonical for execution state; the
notes are regenerated, never hand-edited:

1. Pull in-scope items from the tracker (owner decides scope).
2. Build a manifest (one entry per item: tool, external id, title, status, url,
   container, assignees, due, description).
3. Dry-run the diff first — reports NEW / DRIFTED / OK / STALE. The engine never
   auto-deletes; genuinely closed items are removed by hand.
4. Re-run with `--write-notes` — writes only NEW and DRIFTED reference notes
   (idempotent) and updates the registry.
5. Verify: a clean re-run reports all OK; spot-check one generated note.

The reconcile engine is deliberately offline — it only processes the manifest it is
given ("keys, not prompts"): structural authorization, no ambient network access.

## Trust boundary

The runner proves artifact structure, the current Phase 8 binding, definition-of-done
hash and requirement enforcement, project-local evidence hashes and content scans,
lane and engagement-kind rules, recorded reconciliation, and the owner approval. It does
not independently prove that a client signer had legal authority, that funds settled, or
that a testimonial request was received — those stay owner-attested external facts, but
hollow or placeholder pointers, aliased evidence, and missing evidence files all fail
closed.

Work-surface verification is reported honestly rather than assumed. When a ClickUp API
token is configured, a live task-status check runs and the gate records
`work_surface_verification.mode=live_clickup` **plus the status it actually observed**;
when the token is unset, or for the Linear lane, the mode is `attestation_only` — never
silently presented as live-verified, and never claimed without the lookup having
happened. Terminal ClickUp status names default to `closed`/`complete`/`done` and are
overridable per workspace via a comma-separated environment variable, because ClickUp
statuses are custom per list. Because
`work_surface_verification` describes how the runner was configured rather than what the
owner committed to, it is recorded in the gate for audit but excluded from the content
diff — exporting or unexporting the token never makes a signed gate report itself stale.
The interactive owner-secret prompt is an audit deterrent, not cryptographic identity
authentication.

## Human vs agent

- Agent: prepare and scaffolds, closeout report and retro drafts, evidence assembly and
  scans, archive mechanics, log appends and the compliance check, reconcile runs, gate
  runs.
- Human: client sign-off, invoicing and the payment confirmation, the handoff
  verification, the testimonial and referral ask, the retro judgments and the system
  improvement they commit to, and the gate approval.
