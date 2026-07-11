# Launch-Engagement Automation — Governance Audit

Building an automation is not the same as trusting it. This folder documents the
governance audit the Launch-Engagement Automation is held to: a structured, multi-reviewer
review of every phase of the pipeline before any phase is considered production-trustworthy.

> **Status: in progress.** This is a live audit, not a finished report. The status board
> below reflects the real state — most phases have not yet been reviewed. It is published
> as a working methodology with transparent progress, not as a completed certification.

---

## The method

Each of the eleven pipeline phases is reviewed independently by **five AI engineering
agents**, each assigned a distinct and deliberately narrow role, and then signed off by a
human. Using five different agents with five different mandates surfaces issues that any
single reviewer — however capable — would miss, and keeps the final human sign-off focused
on judgment rather than first-pass discovery.

| Reviewer | Agent | Role | Output |
|----------|-------|------|--------|
| Technical Integrity | Codex | Senior Software Engineer — correctness, reliability, edge cases, security, missing tests | Pass / Pass with Fixes / Fail |
| Architecture | Antigravity | Principal Systems Architect — workflow design, dependencies, failure handling, scalability | Sound / Needs Refinement / Needs Redesign |
| Maintainability | Cursor | Staff DX Engineer — readability, naming, documentation, cognitive load | Easy / Maintainable with Cleanup / Difficult |
| Repository Standards | GitHub Copilot | Repo hygiene, structure, and conventions | — |
| Principal Engineering Review | Claude Code | Final ship call synthesizing all of the above | Score 1–10 + Ship / Ship with Revisions / Redesign |
| Human sign-off | Owner | Final judgment; not delegated | Verified |

The reviewer prompts are in [`prompts/`](prompts/). Four are included verbatim (the fifth,
Repository Standards, is run inside the reviewing IDE).

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

Eleven phases, five reviewers each. As of the last sync:

| # | Phase | Audit state | Automation | Gate | Reviewers done |
|---|-------|-------------|------------|------|----------------|
| 0 | Intake | Reviewing | Hybrid | Keep human | 0 / 5 |
| 1 | Phase 0 — Scaffold | Reviewing | Agent-ready | None | 4 / 5 |
| 2 | Phase 1 — Discovery | Not audited | Hybrid | Keep human | 0 / 5 |
| 3 | Phase 2 — KPI design | Not audited | Hybrid | Keep human | 0 / 5 |
| 4 | Phase 3 — Kit deploy | Not audited | Hybrid | Keep human | 0 / 5 |
| 5 | Phase 4 — Build | Not audited | Manual wall | Removable | 0 / 5 |
| 6 | Phase 5 — QA | Not audited | Hybrid | Keep human | 0 / 5 |
| 7 | Phase 6 — Handoff | Not audited | Hybrid | Keep human | 0 / 5 |
| 8 | Phase 7 — Readout | Not audited | Agent-ready | Keep human | 0 / 5 |
| 9 | Phase 8 — Value | Not audited | Agent-ready | None | 0 / 5 |
| 10 | Phase 9 — Close | Not audited | Hybrid | Keep human | 0 / 5 |

**Summary: 0 of 11 phases verified. 2 in review, 9 not yet started. 1 phase (Scaffold) has
cleared four of its five reviewers.** The board updates as phases are reviewed.

## Why publish an unfinished audit

Because the *framework* is the artifact. A rigorous, multi-reviewer, phase-by-phase audit
methodology — with explicit automation-boundary classification and a human sign-off gate —
is the transferable engineering practice here. The completed findings will follow; the
approach is what makes the automation trustworthy, and it is worth showing in the open with
its real progress rather than waiting to present a polished result.
