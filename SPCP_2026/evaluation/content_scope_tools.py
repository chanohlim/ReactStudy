from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data_utils import data_path, load_json, load_jsonl
from harness import FinalHarness, _f1, _set, _text, run_harness_with_traces, score_dev_submission, validate_payload


class LegacyContentScopeHarness(FinalHarness):
    def build_content_scope(self, task: dict[str, Any], focal: dict[str, Any], control: str, evidence: dict[str, Any]) -> dict[str, Any]:
        attrs = focal.get("attrs") or {}
        contains = {str(x) for x in attrs.get("contains", [])} if isinstance(attrs.get("contains"), list) else set()
        if control == "hold":
            return {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": False}
        if control == "ask":
            return {"mode": "summary", "allowed_fields": ["status"], "excluded_fields": sorted(contains & {"raw_quote", "rrn", "location", "numeric_value", "doctor_note", "card_number"}), "requires_user_confirmation": True}
        if control == "amend" or evidence.get("requires_redaction"):
            excluded = sorted(contains & {"raw_quote", "rrn", "location", "numeric_value", "doctor_note", "card_number", "name"})
            return {"mode": "redacted", "allowed_fields": ["summary", "title", "status"], "excluded_fields": excluded or ["raw_quote"], "requires_user_confirmation": False}
        return {"mode": "summary", "allowed_fields": ["summary", "title", "status"], "excluded_fields": ["raw_quote"], "requires_user_confirmation": False}


class NoLocalStatusScopeHarness(FinalHarness):
    enable_scope_local_status_only = False
class NoRedactedScopeHarness(FinalHarness):
    enable_scope_redacted = False
class NoSummaryScopeHarness(FinalHarness):
    enable_scope_summary = False
class NoNoneScopeHarness(FinalHarness):
    enable_scope_none = False
class NoConfirmationScopeHarness(FinalHarness):
    enable_scope_confirmation = False
class NoFixedSLMScopeHarness(FinalHarness):
    enable_scope_fixed_slm = False


def scope_parts(pred: dict[str, Any], exp: dict[str, Any]) -> dict[str, float]:
    pred = pred if isinstance(pred, dict) else {}
    exp = exp if isinstance(exp, dict) else {}
    return {
        "mode": 1.0 if _text(pred.get("mode")) == _text(exp.get("mode")) else 0.0,
        "allowed_fields": _f1(_set(pred.get("allowed_fields")), _set(exp.get("allowed_fields"))),
        "excluded_fields": _f1(_set(pred.get("excluded_fields")), _set(exp.get("excluded_fields"))),
        "requires_user_confirmation": 1.0 if bool(pred.get("requires_user_confirmation")) == bool(exp.get("requires_user_confirmation")) else 0.0,
    }


def evaluate(cls: type[FinalHarness]) -> dict[str, Any]:
    tasks = load_jsonl(data_path("dev_tasks.jsonl"))
    refs = load_json(data_path("dev_answers.json"))
    payload, _ = run_harness_with_traces(tasks, cls, harness_name=f"scope_{cls.__name__}")
    validate_payload(payload, {str(t["id"]) for t in tasks})
    metrics = score_dev_submission(payload, refs)
    answers = payload["answers"]
    ref_answers = refs["answers"]
    totals = Counter(); sums = Counter(); mode_totals = Counter(); mode_correct = Counter()
    exact_scope = 0; cft = 0; cft_scope_sum = 0.0
    for tid, pred in answers.items():
        exp = ref_answers[tid]
        parts = scope_parts(pred.get("content_scope", {}), exp.get("content_scope", {}))
        for k, v in parts.items():
            sums[k] += v; totals[k] += 1
        if all(v == 1.0 for v in parts.values()):
            exact_scope += 1
        expected_mode = _text(exp.get("content_scope", {}).get("mode"))
        mode_totals[expected_mode] += 1; mode_correct[expected_mode] += int(parts["mode"] == 1.0)
        upstream_ok = pred.get("focal_id") == exp.get("focal_id") and pred.get("target") == exp.get("target") and pred.get("control") == exp.get("control")
        if upstream_ok:
            cft += 1
            cft_scope_sum += 0.40 * parts["mode"] + 0.25 * parts["allowed_fields"] + 0.25 * parts["excluded_fields"] + 0.10 * parts["requires_user_confirmation"]
    return {
        "metrics": metrics,
        "exact_content_scope": exact_scope,
        "content_scope_at_correct_focal_target_control": round(cft_scope_sum / cft, 4) if cft else 0.0,
        "part_accuracy": {k: round(sums[k] / totals[k], 4) for k in sorted(totals)},
        "mode_accuracy": {m: round(mode_correct[m] / mode_totals[m], 4) for m in sorted(mode_totals) if m},
        "payload": payload,
    }


def main() -> None:
    before = evaluate(LegacyContentScopeHarness)
    after = evaluate(FinalHarness)
    variants = {
        "full": after,
        "no_local_status_only": evaluate(NoLocalStatusScopeHarness),
        "no_redacted_scope": evaluate(NoRedactedScopeHarness),
        "no_summary_scope": evaluate(NoSummaryScopeHarness),
        "no_none_scope": evaluate(NoNoneScopeHarness),
        "no_requires_confirmation_logic": evaluate(NoConfirmationScopeHarness),
        "no_fixed_slm_scope_evidence": evaluate(NoFixedSLMScopeHarness),
    }
    rows = []
    for name, row in variants.items():
        m = row["metrics"]
        rows.append(f"| {name} | {m['overall']:.4f} | {m['axes']['focal']:.4f} | {m['axes']['target']:.4f} | {m['axes']['control']:.4f} | {m['axes']['content_scope']:.4f} | {row['exact_content_scope']} | {row['content_scope_at_correct_focal_target_control']:.4f} |")
    lines = [
        "# Content Scope Implementation Summary", "", "This compact summary contains aggregate metrics only; no task-level prediction or trace dumps are committed.", "", "## Before / After",
        f"- Overall: {before['metrics']['overall']:.4f} -> {after['metrics']['overall']:.4f}",
        f"- Focal: {before['metrics']['axes']['focal']:.4f} -> {after['metrics']['axes']['focal']:.4f}",
        f"- Target: {before['metrics']['axes']['target']:.4f} -> {after['metrics']['axes']['target']:.4f}",
        f"- Control: {before['metrics']['axes']['control']:.4f} -> {after['metrics']['axes']['control']:.4f}",
        f"- Content Scope: {before['metrics']['axes']['content_scope']:.4f} -> {after['metrics']['axes']['content_scope']:.4f}",
        f"- Content Scope@Correct Focal+Target+Control: {before['content_scope_at_correct_focal_target_control']:.4f} -> {after['content_scope_at_correct_focal_target_control']:.4f}",
        "", "## Part Accuracy After",
    ]
    for k, v in after["part_accuracy"].items(): lines.append(f"- {k}: {v:.4f}")
    lines += ["", "## Mode Accuracy After"]
    for k, v in after["mode_accuracy"].items(): lines.append(f"- {k}: {v:.4f}")
    lines += ["", "## Ablation", "", "| Variant | Overall | Focal | Target | Control | Content Scope | Exact Scope | Scope@CFT |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |", *rows]
    Path("reports/content_scope_implementation_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

if __name__ == "__main__": main()
