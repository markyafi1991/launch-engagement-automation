# Phase 7 — Readout (client) / case study (portfolio)

Turns the finished build into the decision moment: an executive narrative, a written
decision memo, and a readout deck for clients; an anonymized case study for portfolio
engagements that opt in.

Engine: the `narrative-builder` and `decision-memo` skills plus the readout-deck
procedure, wrapped by the validator's emitted `phase7_commands`. Applies to every
client engagement and to portfolio engagements only when
`include_portfolio_readout: true`. Tool-built-BI additionally requires the recomputed
verified Phase 6 handoff gate.

## Steps

1. **Prepare.** `phase7_commands.prepare` snapshots the prerequisite and
   required-artifact contract into `Deliverables/Readout/phase7.dod.json`. Clients
   receive canonical narrative and memo Markdown scaffolds; portfolios receive a
   project-local copy of the case-study DOCX template. `prepare_force` moves the
   existing Readout directory and gate into a recoverable backup.
2. **Build the narrative** (`narrative-builder` into `Executive_Narrative.md`):
   1. Clarify audience, decision, tone, and desired action.
   2. Extract the core recommendation and supporting logic.
   3. Choose the story pattern (pyramid, SCQA, options, transformation, roadmap).
   4. Build a headline sequence that tells the story by itself.
   5. Prepare hostile questions and answers.
   6. Produce the executive-ready outline: audience and decision, one-sentence core
      message, storyline table (section, headline, purpose), pyramid logic, hostile
      Q&A. Quality bar: the first minute reveals the recommendation; setup language
      that does not help the decision is removed.
3. **Write the decision memo** (`decision-memo` into `Decision_Memo.md`):
   1. Clarify the audience, decision, and required action.
   2. Extract the recommendation and strongest evidence.
   3. Summarize options considered (option, upside, trade-off, verdict).
   4. State risks, mitigations, economics, and next steps.
   5. Draft concisely, answer-first; end with a clear decision request.
   The memo is the leave-behind; the deck is the walk-through.
4. **Generate the deck.** `phase7_commands.generate_pptx` scaffolds
   `Executive_Readout.pptx` from the narrative and memo (meets the slide floor; still
   needs manual polish), finished per the readout-deck procedure:
   - Storyline first — never open the deck tool before the narrative is set.
   - One idea per slide; the headline is the takeaway. Typical arc: situation, the
     gap, the recommendation, the live dashboard screens, economics and value, the ask
     and next steps.
   - House document style; clean, current dashboard screenshots; figures tie to the
     live report; rehearse.
5. **Portfolio route instead:** complete the case-study document using only synthetic
   or public data and explicitly approved sources; anonymization confirmed; real-client
   material never crosses into the portfolio artifact.
6. **Receipts.** `phase7_commands.scaffold_receipts`, then complete `attestation.json`:
   claim rows covering every artifact, bound to current source hashes, using only
   project-local or approved-allowlist sources, citing only approved KPI IDs; delivery
   rows and render confirmations in the same file. Client transfers use an approved
   secure method.
7. **Render and inspect everything.** Client confirmation covers current screenshots,
   number tie-out, recommendation in the first minute, an explicit ask, and rehearsal.
8. **Commit the gate.** `phase7_commands.commit_gate --approved-by <owner>` from an
   interactive owner terminal. The gate rejects unresolved template markers, hollow
   sections or slides, macros, embeddings, ActiveX, external relationships, tracked
   changes, reviewer comments, hidden slides, speaker notes, secrets, local user
   paths, and sensitive-number literals. Success writes `phase7.gate.json` and marks
   Phase 8 ready.

## Trust boundary

The runner verifies structure, hashes, package safety, approved-source and KPI binding,
and recorded human confirmations. It cannot prove the substantive truth of each
citation, that the deck was opened, or that the meeting was rehearsed.

## Human vs agent

- Agent: scaffolds, narrative and memo drafts, deck generation, receipt scaffolding,
  gate runs.
- Human: audience and tone judgment, deck polish, rehearsal, number tie-out
  confirmation, the transfer, and the gate approval.
