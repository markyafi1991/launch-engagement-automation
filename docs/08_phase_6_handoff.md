# Phase 6 — Handoff package

Assembles and gates everything the client (or the portfolio record) actually receives:
the measure dictionary, client handoff documents, citation receipt, and delivery
manifest — each hash-bound so nothing ships except exactly what was QA'd.

Engine: the Phase 6 handoff runner, using the validator's emitted `phase6_commands`.
Tool-built-BI lane only; starts from the verified Phase 5 final-artifact gate.

## Steps

1. **Prepare.** `phase6_commands.prepare` revalidates Phase 5, binds its gate hash,
   snapshots the approved KPI IDs and the exact final TMDL measure names, and writes
   the immutable `Deliverables/Handoff/phase6.dod.json`. It creates a project-local
   Measure Dictionary draft from the seven-column contract. Clients also receive
   project-local copies of the handoff documentation and delivery-checklist DOCX
   templates, whose source hashes are frozen into the DoD; the governed source
   templates are never edited. `prepare_force` restarts by moving the current Handoff
   directory and gate into a timestamped recoverable backup.
2. **Fill the Measure Dictionary** (`Deliverables/Handoff/Measure_Dictionary.md`). The
   seven-column table — KPI ID, Measure, Business meaning, DAX summary, Depends on,
   Format, Display folder — must document every final TMDL measure exactly once, cover
   every approved KPI with at most one KPI ID per row (`N/A` for supporting measures),
   and carry substantive business meaning, conventions, analyst notes, and a named,
   date-stamped review. Unknown KPIs, duplicate KPI citations, extra or missing
   measures, placeholders, and local paths all fail. (The Modeling MCP can draft the
   dictionary from the model; the human reviews.)
3. **Complete the client DOCX package** in Word (clients only). The gate rejects
   macros, embedded binaries and OLE, comments, tracked changes, unresolved
   placeholders, visible Markdown tokens, local-file links, hollow documents, missing
   structured tables, and fake typed tables of contents — real TOC and PAGE fields are
   required. Signature policy: blank signature lines are rejected as unresolved
   placeholders; internal fields are typed and dated before the gate, and the client
   countersigns their own transferred copy after delivery. Render and visually inspect
   the final files before signing the render receipt. Portfolio handoff intentionally
   ships only the internal Measure Dictionary.
4. **Scaffold and fill the receipts.** `phase6_commands.scaffold_receipts` generates:
   - `citation-receipt.json` — records the citation-gate status `ship`, a human
     checker, an artifacts map covering every delivery-manifest file with its current
     hash, and a non-empty claims array (each claim with a stable id, substantive text,
     a citation handle, and status `traceable`), with matching counts and zero
     untraceable claims. Integer-only receipts without claim rows fail closed. This is
     the machine half of the citation gate (see
     [12_cross_cutting.md](12_cross_cutting.md)); the substantive claim check is the
     human half.
   - `delivery-manifest.json` — every shipped file with its current SHA-256, the
     recipient, and a permitted secure transfer method (portfolio uses
     `not_applicable`).
   - clients: `render-receipt.json` — renderer, reviewer, page counts, current hashes,
     and render/visual-review confirmations.
   Re-run scaffolding after any artifact edit, then re-check citations; scaffolding
   deliberately never fabricates a pass.
5. **Commit the gate.** `phase6_commands.commit_gate --approved-by <owner>` from an
   interactive owner terminal (or the split `evidence` / `approve` / `validate` for
   debugging). The runner scans every manifest file for secrets, private keys, bearer
   tokens, local user paths, and sensitive-number patterns. Success writes
   `phase6.evidence.json` and `phase6.gate.json` and marks the next lane-planned phase
   ready. Manifest additions are limited to security-scannable DOCX or text-based
   formats; opaque binaries are rejected.

## Trust boundary

The runner verifies structure, hashes, freshness, package membership, DOCX archive
safety, and recorded attestations. It cannot independently prove that Word was opened,
that each citation handle is substantively correct, or that a transfer reached the
intended recipient — those remain explicit human review.

## Human vs agent

- Agent: prepare, dictionary drafting, receipt scaffolding, scans, gate runs.
- Human: dictionary review, Word completion and visual inspection, citation checking,
  the transfer itself, and the gate approval.
