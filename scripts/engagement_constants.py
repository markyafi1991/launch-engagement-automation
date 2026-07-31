"""Shared engagement metadata enums for start-project and launch-engagement."""

from __future__ import annotations

DATA_CLASSIFICATIONS = (
    "synthetic",
    "public",
    "internal",
    "confidential",
    "financial",
    "phi",
)
SENSITIVE_DATA_CLASSIFICATIONS = ("confidential", "financial", "phi")
ENGAGEMENT_TYPES = ("analytics", "automation", "advisory")
PROJECT_KINDS = ("client", "portfolio")
DELIVERY_LANES = ("tool-built-bi", "software-code", "advisory-only")
CLIENT_STATUSES = ("prospect", "proposal-sent", "active", "delivered", "dormant")
SENSITIVE_PROJECT_PARTS = {"client-comms", "contracts", "intake"}

WORK_SURFACES = {
    "tool-built-bi": "ClickUp Portfolio Projects",
    "software-code": "Linear",
    "advisory-only": "ClickUp business execution",
}

# Orchestration phases a lane does not run. Single source of truth shared by the
# resume guard (intake_normalize) and the phase plan (intake_commands) so the two
# can never disagree about which phases a lane skips. Kit phases (3=kit deploy,
# 4=build, 5=QA, 6=handoff) do not apply to code builds tracked in Linear; phases
# 7-9 (readout/value/close) remain valid resume points for every lane.
SOFTWARE_CODE_SKIP_PHASES = frozenset({3, 4, 5, 6})
ADVISORY_ONLY_SKIP_PHASES = frozenset({3, 4, 5})

# --- Engagement state path: a known limitation of this sanitized extract ---
#
# This extract ships the intake pipeline and Phase 0 only, and it keeps the
# original SINGLE SHARED state file: one ".engagement_state.json" at the root,
# schema version 1.0. That is safe for exactly one engagement at a time.
#
# The private tree replaced this singleton with PER-ENGAGEMENT state: one file
# per engagement at ".engagement_states/<16-hex-digest>.json" (the digest is
# derived from the project path) plus an ".engagement_states/index.json" mapping
# each project path to its digest and state file, at schema version 2. It also
# carries an explicit comment forbidding a shared singleton filename here,
# because a singleton lets one engagement overwrite another's state.
#
# The limitation is stated rather than patched. The per-engagement state layer
# belongs to the Phase 1-9 gate runners, which are not part of this extract, so
# changing these paths in isolation would break the code that is published here
# without delivering the machinery that motivated the change. Anyone running
# more than one engagement concurrently must replace the constants below first.
#
# Canonical engagement state written by launch-engagement validate_intake and
# consumed by start-project via --state-file. Always vault-root relative.
# Do not use .cache/launch-engagement/ — that path is obsolete.
STATE_DIR = "."
STATE_FILENAME = ".engagement_state.json"
ENGAGEMENT_STATE_RELPATH = STATE_FILENAME  # alias for docs / call sites

# Version stamped into .engagement_state.json by the producer (launch-engagement
# validate_intake) and checked by the consumer (start-project build_project). Bump
# the MAJOR component only on a breaking change to the state contract — the consumer
# refuses a state file whose major version it does not understand. Absent version
# (legacy state files) is treated as compatible.
STATE_SCHEMA_VERSION = "1.0"


def phase0_base_relatives(project_path: str) -> list[str]:
    """The base scaffold triple that must exist together (dossier, folder, runbook).

    Single source of truth shared by the create/sync/load detector
    (determine_phase0_action), the partial-scaffold guard
    (validate_phase0_existing_artifacts), and the resume readiness matrix
    (readiness_requirements) so they cannot disagree about what "scaffolded" means.
    """
    return [
        f"{project_path}.md",
        project_path,
        f"{project_path}/SOP Runbook.md",
    ]


def phase0_deliverable_relatives(project_path: str) -> list[str]:
    """The Phase-0 deliverable outputs start-project generates from templates.

    Their presence is what distinguishes load_existing from sync_existing and what
    a Phase-1 resume requires. Keep aligned with build_project ENGAGEMENT_TEMPLATE_FILES.
    """
    return [
        f"{project_path}/Engagement_Runbook.md",
        f"{project_path}/Deliverables/00_Statement_of_Work.md",
        f"{project_path}/Deliverables/00_Brand_and_Design_System.md",
    ]
