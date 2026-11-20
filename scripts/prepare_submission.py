"""Restore exact historical reference paths without changing frozen manifests."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def prepare(root: Path = ROOT) -> None:
    """Verify reference bytes and materialize ignored compatibility documents."""
    root = root.resolve()
    records = json.loads((root / "protocols/reference_files.json").read_text())
    for destination, record in records.items():
        source = (root / record["source"]).resolve()
        target = (root / destination).resolve()
        if not source.is_relative_to(root) or not target.is_relative_to(root / "docs"):
            raise ValueError("Reference path escapes the submission")
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Reference hash mismatch: {source}")
        if target.exists() and target.read_bytes() != data:
            raise ValueError(f"Refusing to overwrite modified reference: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"Verified and prepared {len(records)} historical protocol references.")


if __name__ == "__main__":
    prepare()
