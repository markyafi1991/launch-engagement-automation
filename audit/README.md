# Launch-Engagement Automation — Governance Audit

Building an automation is not the same as trusting it. This folder documents the
governance audit the Launch-Engagement Automation is held to: a structured, multi-reviewer
review of every phase of the pipeline before any phase is considered production-trustworthy.

> **Status: in progress.** This is a live audit, not a finished report. The status board
> below reflects the real state — every phase has cleared its agent reviewers, and none has
> owner sign-off. It is published as a working methodology with transparent progress, not as
> a completed certification.

---

## Release and version

This repository documents the Pack at **Beta**.

Beta is the honest label for: built, multi-reviewer audited, not yet run on a live
engagement.

The Pack is one versioned product, and one number covers all of it — the automation, the
published write-up, this repository's status board, and the private audit database. They
never advertise different versions. The ladder is milestone-driven, not date-driven:

| Version | Meaning |
|---------|---------|
| **Beta** | Pre-battle-test. The release being prepared. Current state. Not yet shipped. |
| **v1** | The first engagement run end to end. |
| **v1.x** | Each audit round that lands changes. |
| **v2** | A structural change to the phase chain or gate model — by definition, regardless of diff size. |
| **v2.x** | The v1.x rule on the v2 line. The pattern is `<major>.<audit-round>`. |

---

## The method

Each of the eleven pipeline phases is reviewed independently by **six AI engineering
agents**, each assigned a distinct and deliberately narrow role, and then signed off by a
human. Using six different agents with six different mandates surfaces issues that any
single reviewer — however capable — would miss, and keeps the final human sign-off focused
on judgment rather than first-pass discovery.

| Reviewer | Agent | Role | Output |
|----------|-------|------|--------|
| Technical Integrity | Codex | Senior Software Engineer — correctness, reliability, edge cases, security, missing tests | Pass / Pass with Fixes / Fail |
| Architecture | Antigravity | Principal Systems Architect — workflow design, dependencies, failure handling, scalability | Sound / Needs Refinement / Needs Redesign |
| Maintainability | Cursor | Staff DX Engineer — readability, naming, documentation, cognitive load | Easy / Maintainable with Cleanup / Difficult |
| Repository Standards | GitHub Copilot | Repo hygiene, structure, and conventions | — |
| Adversarial Review | Grok | Red team — attacks the design, its assumptions, and its cheapest-compliance paths | Survives Contact / Survives with Hardening / Fails Under Pressure |
| Principal Engineering Review | Claude Code | Final ship call synthesizing all of the above | Score 1–10 + Ship / Ship with Revisions / Redesign |
| Human sign-off | Owner | Final judgment; not delegated | Verified |

Maintainability and Adversarial Review are separate seats even though both are run inside
Cursor — Grok is invoked from within the same IDE, and collapsing them into one "Cursor"
row would conflate two reviewers with opposite mandates. (The private audit database names
the Maintainability seat after Cursor's own agent, "Composer", for the same reason.)

## The reviewer prompts

The prompts live in [`prompts/`](prompts/). The canonical stack is **twelve prompts across
two tracks**. Four Track 1 prompts are published here verbatim.

**Track 1 (prompts 1–6) audits built code** — the six seats above, in that order, against an
implementation the reviewer can actually read.

**Track 2 (prompts 7–12) audits proposed control points**, where no implementation exists
yet. The same six seats ask different questions:

| # | Seat | Track 2 question |
|---|------|------------------|
| 7 | Codex | Feasibility — do the modules, fields, commands, and hashes the proposal assumes actually exist? |
| 8 | Antigravity | Architecture fit — does it belong at this layer, or duplicate an existing gate? |
| 9 | Cursor | Handoff quality — could a stranger build this from the spec alone, months later? |
| 10 | GitHub Copilot | Repository and publication surface — file placement, mirrored copies, docs, CI, public repo |
| 11 | Grok | Red team — the catch test, the cheapest-compliance path, source integrity |
| 12 | Claude Code | Version assignment — land in v1, v1.x, or v2; or defer; or kill |

**Do not run Track 1 on a proposal.** A reviewer told to audit code that does not exist will
invent findings rather than report that there is nothing to read. The two-track split exists
specifically to prevent that, and the warning is load-bearing.

## What each phase is classified on

Beyond pass/fail, every phase carries three engineering judgments that make the automation's
boundaries explicit:

- **Automation status** — `Agent-ready`, `Hybrid`, or `Manual wall`. Where the human is, and why.
- **Gate type** — `None`, `Keep human` (a seam kept human on purpose), or `Removable` (a manual
  step worth engineering away).
- **Automation lever** — which levers, if any, would move a `Manual wall` toward `Agent-ready`.

This is the core discipline: an honest automation names the seams it does *not* cross, and
distinguishes the ones that should stay human from the ones that are technical debt.

---

## Live status board

Eleven phases, six agent reviewers each, plus owner sign-off. Every row targets **Beta**. As
of the last sync:

| # | Phase | Audit state | Automation | Gate | Reviewers done |
|---|-------|-------------|------------|------|----------------|
| 0 | Intake | Reviewing | Hybrid | Keep human | 6 / 6 |
| 1 | Phase 0 — Scaffold | Reviewing | Agent-ready | None | 6 / 6 |
| 2 | Phase 1 — Discovery | Reviewing | Hybrid | Keep human | 6 / 6 |
| 3 | Phase 2 — KPI design | Reviewing | Hybrid | Keep human | 6 / 6 |
| 4 | Phase 3 — Kit deploy | Reviewing | Hybrid | Keep human | 6 / 6 |
| 5 | Phase 4 — Build | Reviewing | Manual wall | Removable | 6 / 6 |
| 6 | Phase 5 — QA | Reviewing | Hybrid | Keep human | 6 / 6 |
| 7 | Phase 6 — Handoff | Reviewing | Hybrid | Keep human | 6 / 6 |
| 8 | Phase 7 — Readout | Reviewing | Agent-ready | Keep human | 6 / 6 |
| 9 | Phase 8 — Value | Reviewing | Agent-ready | None | 6 / 6 |
| 10 | Phase 9 — Close | Reviewing | Hybrid | Keep human | 6 / 6 |

**Summary: 0 of 11 phases verified.** All eleven are in review and have cleared all six
agent reviewers. What remains on every one of them is owner sign-off — `Verified` is the
owner's signal, not an agent's, and owner acceptance is outstanding across the board. The
board updates as sign-offs land.

One scope note, so the board is not read for more than it says: the runnable code in this
repository covers the intake pipeline and Phase 0. Phases 1 through 9 are documented here,
not shipped as runnable code. The audit reviews each phase's specification, and the
implementation where an implementation exists.

## Proposed cross-cutting control points

Some findings do not belong to any single phase. Seven are tracked as **proposed control
points** — specifications, not code. None of them is built, and none has been audited yet;
all seven sit at `Not audited` and are reviewed under Track 2 rather than Track 1, for the
reason given above.

| ID | Proposed control point | Target version |
|----|------------------------|----------------|
| C1 | Engagement run trace (decision-level traceability) | v1 |
| C2 | Gate eval corpus (adversarial fixtures) | v1 |
| C3 | Deterministic hook layer (pre-tool-use / stop-validation) | v1.x |
| C4 | Rule-of-Two exposure classification at intake | v1.x |
| C5 | Engagement quarantine and blast-radius report | v2 |
| C6 | Approval risk-tiering (decision-fatigue control) | v2 |
| C7 | Independent reviewer pass (generator / reviewer separation) | v2 |

Round 1 of the audit produced **13 findings** in total. Seven became the control points
above. The remaining six were folded directly into the phase rows they belong to — Phases 0,
1, 4, 5, 6, and 7 — rather than tracked as separate items.

## Why publish an unfinished audit

Because the *framework* is the artifact. A rigorous, multi-reviewer, phase-by-phase audit
methodology — with explicit automation-boundary classification, a two-track prompt stack,
and a human sign-off gate — is the transferable engineering practice here. The completed
findings will follow; the approach is what makes the automation trustworthy, and it is worth
showing in the open with its real progress rather than waiting to present a polished result.
