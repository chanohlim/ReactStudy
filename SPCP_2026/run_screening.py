from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness import FinalHarness, run_harness, validate_payload, write_submission_csv
from data_utils import load_jsonl, data_path


def next_versioned_path(base_dir: Path) -> Path:
    versions: list[int] = []
    for path in base_dir.glob("submission_v*.csv"):
        match = re.fullmatch(r"submission_v(\d+)\.csv", path.name)
        if match:
            versions.append(int(match.group(1)))
    return base_dir / f"submission_v{max(versions, default=0) + 1}.csv"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_submission_csv(path: Path) -> dict[str, Any]:
    csv.field_size_limit(max(csv.field_size_limit(), path.stat().st_size + 1024))
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if len(rows) != 2 or rows[0] != ["submission"] or len(rows[1]) != 1:
        raise ValueError(f"invalid single-cell submission CSV: {path}")
    return json.loads(rows[1][0])


def write_manifest(path: Path, payload: dict[str, Any], expected_ids: set[str], *, generated_at: str) -> Path:
    restored = read_submission_csv(path)
    roundtrip_valid = restored == payload
    validate_payload(restored, expected_ids)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        commit = "unknown"
    stat = path.stat()
    manifest = Path("reports/submission_manifest.md")
    manifest.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Submission Manifest",
        "",
        f"- filename: `{path.name}`",
        f"- harness_commit: `{commit}`",
        f"- generated_at: `{generated_at}`",
        f"- task_count: {len(expected_ids)}",
        f"- answer_count: {len(restored.get('answers', {}))}",
        "- schema_valid: true",
        f"- roundtrip_valid: {str(roundtrip_valid).lower()}",
        f"- file_size_bytes: {stat.st_size}",
        f"- sha256: `{sha256_file(path)}`",
    ]
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not roundtrip_valid:
        raise ValueError("CSV roundtrip did not preserve payload")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SCPC screening submission CSV")
    parser.add_argument("--versioned", action="store_true", help="write the next submission_vN.csv without touching submission.csv")
    parser.add_argument("--output", type=Path, default=None, help="explicit output CSV path")
    args = parser.parse_args()

    tasks = load_jsonl(data_path("screening_tasks.jsonl"))
    expected_ids = {str(t["id"]) for t in tasks}
    payload = run_harness(tasks, FinalHarness, harness_name="python_baseline_screening")
    validate_payload(payload, expected_ids)

    if args.output is not None:
        output = args.output
    elif args.versioned:
        output = next_versioned_path(Path("."))
    else:
        output = Path("submission.csv")
    generated_at = datetime.now(timezone.utc).isoformat()
    write_submission_csv(payload, output)
    manifest = write_manifest(output, payload, expected_ids, generated_at=generated_at)
    print(f"wrote {output}")
    print(f"sha256 {sha256_file(output)}")
    print(f"manifest {manifest}")


if __name__ == "__main__":
    main()
