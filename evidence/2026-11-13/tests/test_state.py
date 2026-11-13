import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock
import engagement_state as state


class StateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = state.new_state_metadata("synthetic/project-a")
        self.path = self.root / state.state_relative_path(self.data["project_path"])

    def test_projects_do_not_overwrite_each_other(self):
        for project in ["synthetic/project-a", "synthetic/project-b"]:
            path = self.root / state.state_relative_path(project)
            state.atomic_write_state(path,state.new_state_metadata(project),expected_revision=0)
        self.assertEqual(len(list((self.root / state.STATE_DIRECTORY).glob("*.json"))),3)
        self.assertEqual(state.load_state(self.path)["project_path"],"synthetic/project-a")

    def test_stale_revision_refused(self):
        state.atomic_write_state(self.path,self.data,expected_revision=0)
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError,"changed concurrently"):
            state.atomic_write_state(self.path,{**self.data,"revision":2},expected_revision=0)
        self.assertEqual(before,self.path.read_bytes())

    def test_private_file_mode(self):
        state.atomic_write_state(self.path,self.data,expected_revision=0)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode),0o600)

    def test_invalid_revisions_rejected(self):
        for revision in [True,0,-1,"1"]:
            with self.subTest(revision=revision):
                self.path.parent.mkdir(exist_ok=True)
                self.path.write_text(json.dumps({**self.data,"revision":revision}))
                with self.assertRaises(ValueError): state.load_state(self.path)

    def test_symlink_read_refused(self):
        self.path.parent.mkdir()
        target=self.root / "fixture.json"
        target.write_text(json.dumps(self.data))
        self.path.symlink_to(target)
        with self.assertRaises(ValueError): state.load_state(self.path)

    def test_failed_replace_preserves_state(self):
        state.atomic_write_state(self.path,self.data,expected_revision=0)
        before=self.path.read_bytes()
        with mock.patch.object(state.os,"replace",side_effect=OSError("synthetic replace failure")):
            with self.assertRaises(OSError):
                state.atomic_write_state(self.path,{**self.data,"revision":2},expected_revision=1)
        self.assertEqual(before,self.path.read_bytes())

    def test_invalid_schema_and_empty_project_refused(self):
        self.path.parent.mkdir()
        for patch in [{"schema_version":999},{"project_path":""}]:
            with self.subTest(patch=patch):
                self.path.write_text(json.dumps({**self.data,**patch}))
                with self.assertRaises(ValueError): state.load_state(self.path)

    def test_revision_check_is_explicitly_optional(self):
        state.atomic_write_state(self.path,self.data,expected_revision=0)
        changed={**self.data,"revision":7}
        state.atomic_write_state(self.path,changed)
        self.assertEqual(state.load_state(self.path)["revision"],7)

    def test_malformed_index_does_not_fail_accepted_state_write(self):
        self.path.parent.mkdir()
        (self.path.parent/state.INDEX_FILENAME).write_text("[]")
        state.atomic_write_state(self.path,self.data,expected_revision=0)
        self.assertEqual(state.load_state(self.path)["revision"],1)
        with self.assertRaisesRegex(ValueError,"root must be an object"):
            state.load_state_index(self.root)


if __name__ == "__main__": unittest.main()
