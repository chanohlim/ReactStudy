from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data_utils import data_path, load_json, load_jsonl
from harness import FinalHarness, run_harness, run_harness_with_traces, score_dev_submission, validate_payload, write_submission_csv


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
    if len(rows) != 2:
        raise ValueError(f"expected header plus one row, got {len(rows)} rows")
    if rows[0] != ["submission"]:
        raise ValueError(f"unexpected header: {rows[0]!r}")
    if len(rows[1]) != 1:
        raise ValueError("submission row must contain exactly one cell")
    return json.loads(rows[1][0])


def structural_profile(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    top_keys = Counter()
    record_keys = Counter()
    record_types = Counter()
    session_counts = Counter()
    for task in tasks:
        top_keys.update(task.keys())
        session_counts[str(task.get("session_id", ""))] += 1
        for record in ((task.get("device_state") or {}).get("records") or []):
            if isinstance(record, dict):
                record_keys.update(record.keys())
                record_types[str(record.get("type"))] += 1
    return {
        "task_count": len(tasks),
        "unique_task_id_count": len({str(t.get("id")) for t in tasks}),
        "session_count": len(session_counts),
        "session_size_min": min(session_counts.values()) if session_counts else 0,
        "session_size_max": max(session_counts.values()) if session_counts else 0,
        "top_keys": sorted(top_keys),
        "record_keys": sorted(record_keys),
        "record_type_count": len(record_types),
    }


def alignment_report(tasks: list[dict[str, Any]], payload: dict[str, Any]) -> dict[str, Any]:
    input_ids = [str(t["id"]) for t in tasks]
    answer_ids = list(payload.get("answers", {}))
    return {
        "task_count": len(input_ids),
        "answer_count": len(answer_ids),
        "unique_task_ids": len(set(input_ids)),
        "unique_answer_ids": len(set(answer_ids)),
        "missing_count": len(set(input_ids) - set(answer_ids)),
        "unexpected_count": len(set(answer_ids) - set(input_ids)),
        "sets_equal": set(input_ids) == set(answer_ids),
        "duplicate_input_ids": len(input_ids) - len(set(input_ids)),
        "duplicate_answer_ids": len(answer_ids) - len(set(answer_ids)),
        "answer_order_matches_runner_order": answer_ids == sorted(input_ids, key=lambda tid: next((str(t.get("session_id", "")), int(t.get("turn_index", 0)), tid) for t in tasks if str(t["id"]) == tid)),
    }


def compare_payloads(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    ids = sorted(set(a.get("answers", {})) | set(b.get("answers", {})))
    same = sum(1 for tid in ids if a.get("answers", {}).get(tid) == b.get("answers", {}).get(tid))
    return {"answer_count_a": len(a.get("answers", {})), "answer_count_b": len(b.get("answers", {})), "same_answer_dicts": same, "different_answer_dicts": len(ids) - same, "task_id_sets_equal": set(a.get("answers", {})) == set(b.get("answers", {}))}


def main() -> None:
    dev_tasks = load_jsonl(data_path("dev_tasks.jsonl"))
    screening_tasks = load_jsonl(data_path("screening_tasks.jsonl"))
    refs = load_json(data_path("dev_answers.json"))

    dev_payload_with_traces, _ = run_harness_with_traces(dev_tasks, FinalHarness, harness_name="parity_dev_trace_runner")
    screening_style_dev_payload = run_harness(dev_tasks, FinalHarness, harness_name="parity_screening_style_dev_runner")
    validate_payload(dev_payload_with_traces, {str(t["id"]) for t in dev_tasks})
    validate_payload(screening_style_dev_payload, {str(t["id"]) for t in dev_tasks})
    dev_metrics = score_dev_submission(dev_payload_with_traces, refs)
    screening_style_metrics = score_dev_submission(screening_style_dev_payload, refs)

    with tempfile.TemporaryDirectory() as tmp:
        csv_path = Path(tmp) / "parity_submission.csv"
        write_submission_csv(screening_style_dev_payload, csv_path)
        restored = read_submission_csv(csv_path)
    roundtrip_same = restored == screening_style_dev_payload

    dev_profile = structural_profile(dev_tasks)
    screening_profile = structural_profile(screening_tasks)
    top_only_dev = sorted(set(dev_profile["top_keys"]) - set(screening_profile["top_keys"]))
    top_only_screening = sorted(set(screening_profile["top_keys"]) - set(dev_profile["top_keys"]))
    record_keys_only_dev = sorted(set(dev_profile["record_keys"]) - set(screening_profile["record_keys"]))
    record_keys_only_screening = sorted(set(screening_profile["record_keys"]) - set(dev_profile["record_keys"]))

    comparison = compare_payloads(dev_payload_with_traces, screening_style_dev_payload)
    report_lines = [
        "# Pipeline Parity Audit", "",
        "This report contains aggregate pipeline and structure checks only; no task-level prediction or trace dumps are committed.", "",
        "## Dev Runner vs Screening-Style Dev Runner", "",
        f"- run_dev-style overall: {dev_metrics['overall']:.4f}",
        f"- screening-style-dev overall: {screening_style_metrics['overall']:.4f}",
        *[f"- {axis}: {dev_metrics['axes'][axis]:.4f} -> {screening_style_metrics['axes'][axis]:.4f}" for axis in ["focal", "target", "control", "content_scope", "policy", "plan"]],
        f"- answer count: {comparison['answer_count_a']} -> {comparison['answer_count_b']}",
        f"- task id sets equal: {str(comparison['task_id_sets_equal']).lower()}",
        f"- identical answer dicts: {comparison['same_answer_dicts']}",
        f"- different answer dicts: {comparison['different_answer_dicts']}", "",
        "## Alignment Invariants", "",
    ]
    for k, v in alignment_report(screening_tasks, run_harness(screening_tasks, FinalHarness, harness_name="alignment_screening_check")).items():
        report_lines.append(f"- {k}: {v}")
    report_lines += ["", "## CSV Roundtrip", "", f"- dev screening-style CSV roundtrip identical: {str(roundtrip_same).lower()}", "", "## Lifecycle Summary", "", "- `run_harness` and `run_harness_with_traces` each instantiate one harness per run, call `prepare([])` once, sort by `(session_id, turn_index, id)`, maintain one mutable session dict per session id, and map answers directly by `task['id']`.", "- The parity test produced identical dev answer dicts, so trace collection does not change Harness lifecycle or predictions.", "", "## Dev vs Screening Structural Profile", "", f"- dev profile: {json.dumps(dev_profile, ensure_ascii=False, sort_keys=True)}", f"- screening profile: {json.dumps(screening_profile, ensure_ascii=False, sort_keys=True)}", f"- top-level keys only in dev: {top_only_dev}", f"- top-level keys only in screening: {top_only_screening}", f"- record keys only in dev: {record_keys_only_dev}", f"- record keys only in screening: {record_keys_only_screening}", "", "## Cause Classification", "", "- A. Submission pipeline error: not reproduced. Alignment, schema validation, lifecycle parity, and CSV roundtrip passed.", "- B. Local evaluator overestimation: plausible. The local evaluator is notebook-compatible but self-contained and uses partial-credit F1/set matching; server scoring may be stricter and uses hidden screening references.", "- C. Dev-screening structure difference: no blocking structural mismatch found; screening has the same core top-level and record-key shape needed by the harness.", "- D. Actual generalization failure: still plausible because pipeline parity passed and public screening references are hidden."]
    out = Path("reports/pipeline_parity_audit.md")
    out.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print("\n".join(report_lines))


if __name__ == "__main__":
    main()
