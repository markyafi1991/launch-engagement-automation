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
CLIENT_STATUSES = ("prospect", "proposal-sent", "active", "delivered", "closed", "dormant")
SENSITIVE_PROJECT_PARTS = {"client-comms", "contracts", "intake"}

WORK_SURFACES = {
    "tool-built-bi": "ClickUp Portfolio Projects",
    "software-code": "Linear",
    "advisory-only": "ClickUp business execution",
}

# Orchestration phases a lane does not run. Single source of truth shared by the
# software-code resume guard (intake_normalize) and phase-plan routing
# (intake_commands). Kit phases (3=kit deploy,
# 4=build, 5=QA, 6=handoff) do not apply to code builds tracked in Linear or to
# advisory-only engagements; phases 7-9 remain valid for every lane.
SOFTWARE_CODE_SKIP_PHASES = frozenset({3, 4, 5, 6})
ADVISORY_ONLY_SKIP_PHASES = frozenset({3, 4, 5, 6})

# Engagement state paths are project-specific and are owned by
# launch-engagement/scripts/engagement_state.py. Do not add a shared singleton
# state filename here: it would allow one engagement to overwrite another.

# On-disk schema version of the per-engagement state JSON. Lives here (the module
# both skill trees import) so the state engine
# (launch-engagement/scripts/engagement_state.py) and the Phase 0 executor
# (start-project/scripts/build_project.py) can never disagree about which schema
# they read/write. Bump in lockstep with any breaking state-shape change.
STATE_SCHEMA_VERSION = 2

# Milestone gate count for tool-built BI engagements in ClickUp Portfolio Projects.
# Matches the engagement runbook arc (Engagement set up → Discovery → M0–M5 →
# Recommendation → Value → Engagement closed). Keep aligned with
# launch-engagement/scripts/clickup_blueprints.json milestone_name_patterns.
ENGAGEMENT_MILESTONE_GATE_COUNT = 11
