"""Versioned, per-engagement state with atomic and private persistence.

State files live at ``.engagement_states/<16-hex-digest>.json`` where the digest
is ``sha256(project_path)[:16]``. A human-readable map is maintained at
``.engagement_states/index.json`` (project_path → digest / state_file).
"""

from __future__ import annotations

import hashlib
import fcntl
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))



from engagement_constants import STATE_SCHEMA_VERSION

STATE_DIRECTORY = ".engagement_states"
INDEX_FILENAME = "index.json"
INDEX_SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_digest(project_path: str) -> str:
    return hashlib.sha256(project_path.encode("utf-8")).hexdigest()[:16]


def state_relative_path(project_path: str) -> str:
    return f"{STATE_DIRECTORY}/{project_digest(project_path)}.json"


def index_relative_path() -> str:
    return f"{STATE_DIRECTORY}/{INDEX_FILENAME}"


def new_state_metadata(project_path: str) -> dict[str, Any]:
    return {
        "schema_version": STATE_SCHEMA_VERSION,
        "engagement_id": str(uuid4()),
        "revision": 1,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "project_path": project_path,
        "phase_status": {str(phase): "pending" for phase in range(10)},
    }


def load_state(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"State must be a regular, non-symlink file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid engagement state {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Engagement state JSON root must be an object: {path}")
    if data.get("schema_version") != STATE_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported state schema {data.get('schema_version')!r}; "
            f"expected {STATE_SCHEMA_VERSION}. Re-run intake validation."
        )
    revision = data.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise ValueError("Engagement state revision must be a positive integer.")
    if not isinstance(data.get("project_path"), str) or not data["project_path"].strip():
        raise ValueError("Engagement state project_path must be a non-empty string.")
    return data


def _write_private_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        os.chmod(path, 0o600)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def load_state_index(root: Path) -> dict[str, Any]:
    path = root / index_relative_path()
    if not path.exists():
        return {
            "schema_version": INDEX_SCHEMA_VERSION,
            "updated_at": utc_now(),
            "by_digest": {},
            "by_project_path": {},
        }
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"State index must be a regular, non-symlink file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid engagement state index {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Engagement state index JSON root must be an object.")
    data.setdefault("by_digest", {})
    data.setdefault("by_project_path", {})
    data["schema_version"] = INDEX_SCHEMA_VERSION
    return data


def upsert_state_index(root: Path, state_path: Path, state: dict[str, Any]) -> None:
    """Record a state file in the human-readable index (no-op for index.json itself)."""
    if state_path.name == INDEX_FILENAME:
        return
    try:
        relative = state_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return
    if not relative.startswith(f"{STATE_DIRECTORY}/"):
        return
    project_path = str(state.get("project_path") or "")
    if not project_path:
        return
    digest = project_digest(project_path)
    entry = {
        "digest": digest,
        "project_path": project_path,
        "state_file": relative,
        "engagement_id": state.get("engagement_id"),
        "updated_at": state.get("updated_at") or utc_now(),
        "revision": state.get("revision"),
    }
    index = load_state_index(root)
    index["by_digest"][digest] = entry
    index["by_project_path"][project_path] = entry
    index["updated_at"] = utc_now()
    _write_private_json(root / index_relative_path(), index)


def rebuild_state_index(root: Path) -> dict[str, Any]:
    """Rescan ``.engagement_states/*.json`` (excluding index) and rewrite the index."""
    state_dir = root / STATE_DIRECTORY
    index: dict[str, Any] = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "updated_at": utc_now(),
        "by_digest": {},
        "by_project_path": {},
    }
    if not state_dir.is_dir():
        _write_private_json(root / index_relative_path(), index)
        return index
    for path in sorted(state_dir.glob("*.json")):
        if path.name == INDEX_FILENAME or path.is_symlink():
            continue
        try:
            state = load_state(path)
        except ValueError:
            continue
        project_path = str(state.get("project_path") or "")
        if not project_path:
            continue
        digest = project_digest(project_path)
        entry = {
            "digest": digest,
            "project_path": project_path,
            "state_file": path.relative_to(root).as_posix(),
            "engagement_id": state.get("engagement_id"),
            "updated_at": state.get("updated_at") or utc_now(),
            "revision": state.get("revision"),
        }
        index["by_digest"][digest] = entry
        index["by_project_path"][project_path] = entry
    index["updated_at"] = utc_now()
    _write_private_json(root / index_relative_path(), index)
    return index


def lookup_state_file(root: Path, project_path: str) -> str:
    """Return the relative state path for a project (from index when present)."""
    index = load_state_index(root)
    entry = index.get("by_project_path", {}).get(project_path)
    if isinstance(entry, dict) and entry.get("state_file"):
        return str(entry["state_file"])
    return state_relative_path(project_path)


def atomic_write_state(
    path: Path, data: dict[str, Any], *, expected_revision: int | None = None
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        if expected_revision is not None:
            current_revision = 0
            if path.exists():
                current = load_state(path)
                current_revision = int(current.get("revision", 0))
            if current_revision != expected_revision:
                raise ValueError(
                    "Engagement state changed concurrently; reload and retry the operation."
                )
        fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        temporary_path = Path(temporary)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
            os.chmod(path, 0o600)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
        # Best-effort human index; never fail the state write if index update fails.
        try:
            root = path.parent.parent
            if path.parent.name == STATE_DIRECTORY:
                upsert_state_index(root, path, data)
        except (OSError, ValueError, TypeError):
            pass
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


def merge_existing_metadata(path: Path, state: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return state
    existing = load_state(path)
    if existing.get("project_path") != state.get("project_path"):
        raise ValueError("State-path collision: existing state belongs to another project.")
    state["engagement_id"] = existing["engagement_id"]
    state["created_at"] = existing["created_at"]
    state["revision"] = int(existing.get("revision", 0)) + 1
    phase_status = dict(state.get("phase_status") or {})
    existing_status = existing.get("phase_status")
    if isinstance(existing_status, dict):
        phase_status.update(existing_status)
    state["phase_status"] = phase_status
    for phase_key in (
        "discovery",
        "kpi_design",
        "phase4",
        "phase5",
        "phase6",
        "phase7",
        "phase8",
        "phase9",
    ):
        if phase_key in existing:
            state[phase_key] = existing[phase_key]
    if "engagement_status" in existing:
        state["engagement_status"] = existing["engagement_status"]
    state["updated_at"] = utc_now()
    return state
