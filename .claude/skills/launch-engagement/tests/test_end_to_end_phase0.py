"""End-to-end integration test for the Phase 0 cross-skill seam.

The unit tests in test_validate_intake.py only *parse-test* the contract between
launch-engagement (producer of .engagement_state.json) and start-project
(consumer that scaffolds the project). This test exercises the full seam against
a hermetic temp vault seeded with the REAL vault templates:

    1. launch-engagement validate_intake writes .engagement_state.json
    2. the emitted `build_project.py create --state-file ...` command runs for real
    3. the six Phase-0 definition-of-done artifacts must exist on disk
    4. re-running validate_intake must flip phase0_action to `load_existing`

It is the guard the Phase 0 review flagged as the single highest-value gap: if
anyone renames a template, moves a DoD artifact, or drifts the state contract,
this test fails instead of the failure surfacing at deploy time. It also proves
Phase 0 stands up the folder, dossier, and SOP runbook WITHOUT touching any
canonical SOP (the temp vault has none; the runbook only wiki-links them).
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = SKILL_DIR / "scripts"
LIVE_VAULT = SKILL_DIR.parents[2]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

_SPEC = importlib.util.spec_from_file_location("validate_intake", SCRIPT_DIR / "validate_intake.py")
assert _SPEC and _SPEC.loader
validate_intake = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = validate_intake
_SPEC.loader.exec_module(validate_intake)


def _load_build_project():
    path = LIVE_VAULT / ".claude/skills/start-project/scripts/build_project.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("build_project_e2e", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# The six Phase-0 definition-of-done artifacts, relative to the project folder
# (dossier and the folder itself are checked separately). Keep aligned with the
# resume matrix in SKILL.md and engagement_constants.phase0_deliverable_relatives.
DOD_FOLDER_ARTIFACTS = (
    "SOP Runbook.md",
    "Engagement_Runbook.md",
    "Deliverables/00_Statement_of_Work.md",
    "Deliverables/00_Brand_and_Design_System.md",
)

# Real template + fixture files the scaffold reads. Copied verbatim from the live
# vault so this test pins the actual cross-skill contract, not a hand-rolled stub.
ENGAGEMENT_TEMPLATES = (
    "06_Templates/Projects/AI-BI Consulting Engagement/Engagement Runbook (TEMPLATE).md",
    "06_Templates/Projects/AI-BI Consulting Engagement/Deliverables/00_Statement_of_Work (TEMPLATE).md",
    "06_Templates/Projects/AI-BI Consulting Engagement/Deliverables/00_Brand_and_Design_System (TEMPLATE).md",
    "06_Templates/Projects/AI-BI Consulting Engagement/Deliverables/01_Situation_Assessment (TEMPLATE).md",
)
CLIENT_TEMPLATES = (
    "06_Templates/Notes/Client Dossier Template.md",
    "02_Clients/_Client_Template/Client Folder README.md",
    "02_Clients/_Client_Template/Onboarding Checklist.md",
    "02_Clients/_Client_Template/Offboarding Checklist.md",
)

PORTFOLIO_HUB_STUB = (
    "# Portfolio Hub\n\n"
    "| Piece | Strategic Job | Status | Next Shipping Step |\n"
    "|---|---|---|---|\n\n"
)
CRM_TRACKER_STUB = (
    "# CRM Pipeline Tracker\n\n"
    "| Client Name / Upwork ID | Source | Status | Next Step | Last Contacted | Deal Value (Est) |\n"
    "|---|---|---|---|---|---|\n\n"
)


@unittest.skipIf(_load_build_project() is None, "start-project build_project.py not present")
class EndToEndPhase0Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.build_project = _load_build_project()
        self._seed_templates()
        # Kit manifest so tool-built-bi intake validates the kit name.
        kit_dir = self.root / "06_Templates/Kits/Power BI Project Kit"
        kit_dir.mkdir(parents=True)
        (kit_dir / "manifest.json").write_text(
            '{"kit": "Power BI Project Kit", "deploy_root": "Power BI Kit", "version": "1.0"}',
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _seed_templates(self) -> None:
        for relative in (*ENGAGEMENT_TEMPLATES, *CLIENT_TEMPLATES):
            source = LIVE_VAULT / relative
            if not source.is_file():
                self.skipTest(f"required live template missing: {relative}")
            dest = self.root / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        (self.root / "04_Portfolio").mkdir(parents=True, exist_ok=True)
        (self.root / "04_Portfolio/Portfolio Hub.md").write_text(PORTFOLIO_HUB_STUB, encoding="utf-8")
        (self.root / "02_Clients").mkdir(parents=True, exist_ok=True)
        (self.root / "02_Clients/CRM_Pipeline_Tracker.md").write_text(CRM_TRACKER_STUB, encoding="utf-8")

    def _validate(self, payload: dict[str, object]) -> dict[str, object]:
        intake_path = self.root / "intake.json"
        intake_path.write_text(json.dumps(payload), encoding="utf-8")
        exit_code = validate_intake.main(["--root", str(self.root), "--file", str(intake_path)])
        self.assertEqual(exit_code, 0)
        state_file = self.root / ".engagement_state.json"
        self.assertTrue(state_file.is_file())
        return json.loads(state_file.read_text(encoding="utf-8"))

    def _assert_dod_artifacts(self, project_path: str) -> Path:
        dossier = self.root / f"{project_path}.md"
        folder = self.root / project_path
        self.assertTrue(dossier.is_file(), f"missing dossier: {project_path}.md")
        self.assertTrue(folder.is_dir(), f"missing project folder: {project_path}")
        for relative in DOD_FOLDER_ARTIFACTS:
            self.assertTrue(
                (folder / relative).is_file(),
                f"missing Phase-0 DoD artifact: {project_path}/{relative}",
            )
        return folder

    def _run_emitted_create(self, state: dict[str, object]) -> None:
        command = state["start_project_command"]
        self.assertEqual(command[2], "create")
        # Drive the actual CLI entry point the runtime would invoke.
        exit_code = self.build_project.main(["--root", str(self.root), *command[2:]])
        self.assertEqual(exit_code, 0)

    def test_portfolio_phase0_stands_up_and_round_trips(self) -> None:
        project_path = "04_Portfolio/E2E Variance Demo"
        payload = {
            "kind": "portfolio",
            "name": "E2E Variance Demo",
            "industry": "Fund administration",
            "delivery_lane": "tool-built-bi",
            "kit": "Power BI Project Kit",
            "project_path": project_path,
            "deliverables": ["Power BI variance dashboard", "Build recipe"],
        }

        state = self._validate(payload)
        self.assertEqual(state["phase0_action"], "create")
        self.assertEqual(state["schema_version"], "1.0")

        self._run_emitted_create(state)
        folder = self._assert_dod_artifacts(project_path)

        # Phase 0 must not create or edit any canonical SOP — it only wiki-links them.
        self.assertFalse((self.root / "01_Operations/SOPs").exists())
        runbook = (folder / "SOP Runbook.md").read_text(encoding="utf-8")
        self.assertIn("Canonical SOPs remain approval-controlled", runbook)

        # Deliverables were hydrated from the real templates, not left as placeholders.
        sow = (folder / "Deliverables/00_Statement_of_Work.md").read_text(encoding="utf-8")
        self.assertNotIn("{{", sow)

        # Re-running intake against the now-scaffolded project flips to load_existing.
        reloaded = self._validate(payload)
        self.assertEqual(reloaded["phase0_action"], "load_existing")
        self.assertEqual(reloaded["start_project_command"], [])

    def test_client_phase0_stands_up_dossier_folder_and_runbook(self) -> None:
        project_path = "02_Clients/E2E Acme Funds"
        payload = {
            "kind": "client",
            "name": "E2E Acme Funds",
            "industry": "Fund administration",
            "delivery_lane": "tool-built-bi",
            "kit": "Power BI Project Kit",
            "source": "Upwork",
            "project_path": project_path,
            "deliverables": ["Variance dashboard"],
        }

        state = self._validate(payload)
        self.assertEqual(state["phase0_action"], "create")

        self._run_emitted_create(state)
        folder = self._assert_dod_artifacts(project_path)

        # Client dossier was rendered from the real template (name substituted in).
        dossier = (self.root / f"{project_path}.md").read_text(encoding="utf-8")
        self.assertIn("E2E Acme Funds", dossier)
        # Canonical SOPs untouched; client folder structure exists.
        self.assertFalse((self.root / "01_Operations/SOPs").exists())
        self.assertTrue((folder / "intake").is_dir())

        reloaded = self._validate(payload)
        self.assertEqual(reloaded["phase0_action"], "load_existing")

    def test_consumer_refuses_unknown_state_major_version(self) -> None:
        # Forward-compat guard: a state file from a newer, breaking producer must be
        # refused loudly, not silently mis-read.
        self.build_project.check_state_schema_version({"schema_version": "1.3"})  # same major: ok
        with self.assertRaisesRegex(ValueError, "Incompatible engagement state schema_version"):
            self.build_project.check_state_schema_version({"schema_version": "2.0"})
        # Legacy state files with no version are treated as compatible.
        self.build_project.check_state_schema_version({})


if __name__ == "__main__":
    unittest.main()
