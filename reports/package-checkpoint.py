#!/usr/bin/env python3
"""Build separate public-source and confidential-continuation checkpoint ZIPs."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import zipfile
from datetime import datetime, timezone


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args])


def forbidden_public_path(name: str) -> bool:
    p = Path(name)
    lower = name.lower()
    return (
        any(part in {".private", ".git", "node_modules", "target", "__pycache__"} for part in p.parts)
        or ("keypair" in lower and p.suffix.lower() not in {".c", ".h", ".rs", ".py", ".ts", ".md"})
        or p.suffix.lower() in {".sqlite", ".sqlite3", ".db", ".pem", ".key"}
        or p.name.lower().startswith("signer-journal")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confidential", type=Path)
    parser.add_argument("--allow-in-progress", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    dirty = git(repo, "status", "--porcelain", "--untracked-files=all").decode().splitlines()
    if dirty and not args.allow_in_progress:
        raise SystemExit("Refusing a public checkpoint from an uncommitted tree; commit owned source/evidence first.")
    commit = git(repo, "rev-parse", "HEAD").decode().strip()
    archive = git(repo, "archive", "--format=zip", "HEAD")
    digest_map = {}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(archive)) as source, zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as target:
        for entry in source.infolist():
            if forbidden_public_path(entry.filename):
                raise SystemExit("Tracked private/build path cannot enter public checkpoint: " + entry.filename)
            payload = source.read(entry.filename)
            target.writestr("solana-bunker/" + entry.filename, payload)
            if not entry.is_dir():
                digest_map[entry.filename] = hashlib.sha256(payload).hexdigest()
        target.writestr("solana-bunker/CHECKPOINT_MANIFEST.json", json.dumps({
            "schema_version": 1,
            "source_commit": commit,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "Public source/evidence checkpoint; no live credentials or signer journals",
            "working_tree_in_progress": bool(dirty),
            "uncommitted_work_excluded": bool(dirty),
            "files_sha256": digest_map,
        }, indent=2) + "\n")
    if args.confidential:
        private = repo / ".private"
        args.confidential.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.confidential, "w", zipfile.ZIP_DEFLATED) as target:
            for path in sorted(private.rglob("*")):
                if path.is_file() and not path.is_symlink():
                    target.write(path, "solana-bunker/.private/" + str(path.relative_to(private)))
            target.writestr("CONFIDENTIAL_README.md", (
                "# Confidential development continuity\n\n"
                "Contains live development credentials and possibly signing journals. Do not publish or share.\n"
                "Restore .private only to the same source checkpoint with directory permissions700 and files600.\n"
                "Source commit: " + commit + "\n"
                "Verify wallet public address/cluster before funding or deployment. Never restore an old signing journal over newer state.\n"
                "If any signing state is uncertain, abandon affected leaves/use a fresh keyset instead of reusing them.\n"
            ))
        os.chmod(args.confidential, 0o600)
    print(json.dumps({"public_path": str(args.output.resolve()), "source_commit": commit,
        "public_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "confidential_path": str(args.confidential.resolve()) if args.confidential else None}))


if __name__ == "__main__":
    main()
