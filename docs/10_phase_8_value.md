# Phase 8 — Value realization

Moves the engagement from promised value to captured value: who owns each benefit, how
it is measured, against what baseline, out of which source document, on what rhythm —
bound into an immutable definition of done and a gate that re-reads the cited sources
rather than taking the ledger's word for them.

Engine: the Phase 8 value runner, using the validator's emitted `phase8_commands`, with
the `value-realization` skill filling the artifacts. Phase 8 applies to every lane. It
starts from the current approved KPI design and, when Phase 7 applies, from the
recomputed verified Phase 7 gate.

## Steps

1. **Prepare.** `phase8_commands.prepare` writes the immutable
   `Deliverables/Value/phase8.dod.json` and the two canonical drafts:
   `Value_Realization_Plan.md` and `How_to_Read_the_Value_Ledger.md`. `prepare_force`
   moves any existing output and gate into a recoverable `Value.rolledback-<UTC>`
   directory; those backups are retained until they are manually reviewed and removed.
2. **Fill the plan** (`value-realization`): value ambition and benefit categories,
   value drivers and initiatives, owners and measurement methods — owners for value,
   not only activity — baselines, targets and timing with one-time and recurring
   benefits separated, governance and escalation triggers, and the risks to capture.
3. **Write every ledger row to contract.** Each row requires:
   - a unique `VAL-NNN` id (duplicates fail);
   - one-time or recurring classification;
   - baseline and target amounts, plus the unit — amounts accept the shapes a source
     document actually uses (`10`, `1,000`, `$1,200,000`, `12%`), with the denomination
     still carried in `Unit`;
   - the number of periods and a target date;
   - a named value owner and a named measurement owner;
   - at least one approved `KPI-NNN`;
   - an exact source path drawn from the intake's approved-sources allowlist;
   - a proof standard, a controlled measurement cadence, and a confidence level.
4. **Define governance.** Participants, decision rights, an escalation trigger, and
   **a forum for every cadence the ledger promises** — a ledger that commits to a
   monthly measurement rhythm with no monthly forum behind it fails the gate.
5. **Commit the gate.** `phase8_commands.commit_gate --approved-by <owner>` from an
   interactive owner terminal, or the split `evidence` / `approve` / `validate`
   commands when debugging. The gate source-hashes every cited allowlisted file and
   requires each baseline to appear in the source it cites (headings and calendar dates
   excluded, and narrowed to a heading anchor when the citation gives one). It binds
   each row's baseline-to-target movement to the approved KPI's favorable direction, and
   rejects past target dates, one-time rows carrying a weekly cadence, ledger cadences
   with no governance forum, duplicate `VAL-NNN`, unresolved markers (including skill
   bracket stubs), realized-value claim language, unknown KPIs, off-allowlist sources,
   definition-of-done tampering after prepare, symlinked artifact paths, secrets, local
   user paths, and sensitive-number literals where applicable.
6. **Success** writes `phase8.gate.json` — carrying the structured ledger *and* the
   governance model — marks Phase 8 complete, and marks Phase 9 ready. Any artifact,
   source, KPI, readout, evidence, approval, or definition-of-done drift invalidates
   resume, and Phase 9 cannot start without the recomputed gate.
7. **To change or re-approve an already-gated phase, reopen — do not force-prepare.**
   `reopen` returns the phase to in-progress, keeps the artifacts and the frozen
   definition of done, and files the prior approval under `superseded_approvals`;
   `prepare --force` archives the work and re-scaffolds placeholders. Reopen is the
   remedy when an approval ages past the 14-day limit. Downstream stays blocked while a
   phase is reopened. The same command exists on Phases 6, 7, and 9.

## Output

The Value Realization Plan:

- **Value Ambition** — target value and timing.
- **Value Ledger** — one contract-complete row per benefit (id, type, baseline, target,
  unit, periods, target date, value and measurement owners, KPI IDs, source path, proof
  standard, cadence, confidence).
- **Governance** — cadence, participants, decision rights, escalation trigger.
- **Risks To Capture.**

Plus `How_to_Read_the_Value_Ledger.md`, the one-pager that lets the client operate the
ledger without the consultant in the room.

## Quality bar

- Baseline and target defined for every benefit, each traceable to an allowlisted
  source document that actually contains the baseline figure.
- Owners assigned for value, not only activity — and measurement owned separately from
  the benefit itself.
- One-time and recurring benefits separated, with a cadence that matches the type.
- Every KPI cited is an approved KPI, and the promised movement runs in that KPI's
  favorable direction.
- Governance covers every cadence the ledger promises, with escalation triggers.
- The plan forecasts value; it never claims value already realized.

## Authoring-time vs invariant rules

Phase 8 deliberately separates rules that constrain what the owner may commit to *now*
from rules that must hold for the life of the gate. "Target date must not be in the
past" is authoring-time only: a verified gate does not fail later merely because a date
it committed to has since arrived — that is the value plan working as intended.
Everything else — structure, hashes, source and KPI binding, safety scans, approval age
— is an invariant and is re-checked on every resume.

## Trust boundary

The runner verifies structure, hashes, source/KPI/direction binding, definition-of-done
integrity, safety scans, and the recorded owner approval. It does not prove the business
truth of a baseline attribution or a forecast beyond requiring the baseline numeral to
appear in the cited source — that is a numeral search, not a semantic one, so a small
integer can still coincide with unrelated prose even after headings and dates are
excluded. KPIs whose favorable direction is `target` or `range` are not movement-checked
at all, because the band lives in free-text threshold prose the runner cannot parse;
those stay owner judgment. The interactive owner-secret prompt is an audit deterrent,
not cryptographic identity authentication.

## Human vs agent

- Agent: prepare, the plan and one-pager drafts, ledger and governance assembly, source
  and KPI binding, scans, gate runs.
- Human: the value ambition, named benefit and measurement owners, the baseline
  attribution and forecast judgment, band-based KPI judgment the runner cannot check,
  participation in the governance cadence itself, and the gate approval.
