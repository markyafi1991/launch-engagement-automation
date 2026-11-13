"""Demonstrate two synthetic engagements and stale-revision refusal."""
import json
from pathlib import Path
import tempfile
import engagement_state as state


def main():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        paths = ["synthetic/project-a", "synthetic/project-b"]
        for project in paths:
            state.atomic_write_state(root / state.state_relative_path(project), state.new_state_metadata(project), expected_revision=0)
        path = root / state.state_relative_path(paths[0])
        current = state.load_state(path)
        current["revision"] += 1
        state.atomic_write_state(path, current, expected_revision=1)
        refused = False
        try:
            state.atomic_write_state(path, current, expected_revision=1)
        except ValueError:
            refused = True
        print(json.dumps({"synthetic":True,"separate_paths":len(set(state.state_relative_path(p) for p in paths))==2,
                          "stale_revision_refused":refused,"schema":current["schema_version"],
                          "end_to_end_engagement":False,"v1_shipped":False}, indent=2))


if __name__ == "__main__":
    main()
