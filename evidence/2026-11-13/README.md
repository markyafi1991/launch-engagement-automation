---
version: "1.0"
created: 2026-11-13
updated: 2026-11-13
---

# Current state-handling evidence slice

**Version 1.0** · 2026-11-13

This additive slice demonstrates the current per-engagement state primitive.
It is separate from the historical Beta extract at the repository root: the old
extract's singleton state and incomplete phase machinery remain its actual limits.
The complete private phase engine has not been copied or represented as shipped.

From this directory:

```sh
python3 -B -m unittest discover -s tests -v
python3 -B demo.py
```

Python 3.10+ on macOS/Linux (`fcntl` locking). The demo uses two invented
engagements in a temporary folder. Tests check separate paths, stale-revision
refusal, mode 0600, invalid schema metadata, symlink reads and failed replacement.
`engagement_state.py` is copied from the working engine with only the vault
bootstrap import removed. Sibling constants are supplied unchanged.
[Source hashes](PROVENANCE.json) · [Tests](tests/test_state.py).

The state primitive is not a signed approval, external attestation, full delivery
workflow or complete package standard. Its human-readable index is best-effort;
an index update failure does not undo an accepted state write. POSIX local file
locking does not establish cross-host transaction safety. Owner acceptance and
an end-to-end v1 engagement remain separate gates.

Stale-revision protection is opt-in: callers must supply `expected_revision`.
Calls that omit it can overwrite state without a revision comparison. A small
source fix included here rejects a non-object JSON index with `ValueError`, so
the documented best-effort index path can preserve an accepted state write.

See [report connection](REPORT.md), [claim map](evidence-map.json),
and [publication review](PUBLICATION_REVIEW.md). Cite the immutable evidence commit
or its release archive, not an evolving branch or a private regression total.
