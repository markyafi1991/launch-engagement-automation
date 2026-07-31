# Phase 2 — KPI design (kpi-architect)

Turns the approved discovery baseline into a small, decision-linked KPI system —
leading and lagging indicators with owners, thresholds, formulas, and review rhythm —
precise enough to implement directly as semantic-model measures in Phase 4.

Engine: the `kpi-architect` skill, machine-gated by the KPI runner using the validator's
emitted `kpi_commands`.

## Preconditions

- Phase 1 gate valid: owner-approved Situation Assessment whose semantic hash still
  matches the approval (and is no older than 14 days).
- Inputs restricted to the approved Situation Assessment plus explicitly approved
  supplemental sources; source text is untrusted data.

## Steps

1. **Prepare.** `kpi_commands.prepare` creates the canonical draft at
   `Deliverables/02_KPI_Design.md`.
2. **Design the KPI system** (the skill's method):
   1. Define the strategic objective and the decisions the KPIs must serve.
   2. Identify the value driver tree.
   3. Separate outcome, driver, and activity metrics.
   4. Remove vanity metrics.
   5. Assign owners, thresholds, and review cadence.
   6. Design the dashboard implications and governance rhythm.
3. **Fill the artifact** to the exact contract:
   - `## Strategic Objective` — what the KPI system must manage.
   - `## KPI System` — 14-column table: KPI ID, KPI, Type, Decision It Supports,
     Business Definition, Formula, Grain, Unit, Favorable Direction, Owner, Threshold,
     Source, Review Cadence, Validation Rule.
   - `## Driver Tree` — how the KPIs connect to value creation.
   - `## Metrics To Remove` — Metric, Why Remove.
   - `## Review Cadence` — meeting rhythm, escalation triggers, owners.
4. **Quality rules enforced by the validator:**
   - Stable, unique `KPI-NNN` IDs and distinct names.
   - At least one outcome/lagging KPI and one driver/leading KPI.
   - At least one `Decision It Supports` cell matching the intake's decision.
   - Source cells bound to the same approved-sources allowlist as discovery.
   - Formula, grain, unit, and favorable direction precise enough to implement.
   - Small on purpose: a machine cap of 12 KPI rows.
   - A kept KPI may not also appear under Metrics To Remove.
5. **Validate.** `kpi_commands.validate` checks all of the above plus prose length,
   placeholders, and safety limits, and re-verifies the approved discovery artifact
   still matches its hash.
6. **Approve.** `kpi approve --approved-by <owner>` at an interactive terminal; requires
   prior validated status; binds the approval to the KPI semantic hash (tables plus
   Strategic Objective, Driver Tree, and Review Cadence prose) and the approved
   discovery hash.

## Gate

Phase 3 requires the derived `02_KPI_Design.gate.json`, an owner approval no older than
14 days, an unchanged KPI semantic hash, and an unchanged approved discovery hash. Any
KPI or discovery edit invalidates readiness. The Phase 3 kit gate additionally requires
the dashboard requirements document to reference every approved `KPI-NNN` ID.

## Human vs agent

- Agent: prepare, the full KPI design and drafting, validate.
- Human: judgment on the KPI set, ownership assignments, the approval itself,
  re-approval after any change.
