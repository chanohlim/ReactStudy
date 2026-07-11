from __future__ import annotations

import importlib.util
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data_utils import data_path, load_json, load_jsonl
from harness import FinalHarness, _f1, _plan_score, _policy_score, _set, run_harness_with_traces, score_dev_submission, validate_payload
from harness import records_of, text_of


class LegacyPolicyPlanHarness(FinalHarness):
    def build_policy(self, task: dict[str, Any], focal: dict[str, Any], target: str, control: str, scope: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        violations = set()
        values = " ".join(text_of(r.get("value")) for r in records_of(task)).lower()
        if "revoked" in values or "철회" in values:
            violations.add("consent_revoked")
        if "phishing" in values or "피싱" in values:
            violations.add("security_alert_ignored")
        return {"risk_flags": sorted(evidence.get("risk_flags", [])), "violations": sorted(violations), "requires_confirmation": control == "ask"}

    def build_plan_events(self, task: dict[str, Any], focal_id: str, target: str, control: str, scope: dict[str, Any], policy: dict[str, Any]) -> list[dict[str, Any]]:
        events = [{"verb": "read", "target": focal_id, "args": {"purpose": "inspect_task_context"}}]
        if control == "hold":
            events.append({"verb": "guard", "target": focal_id, "args": {"reason": "safety_or_policy"}})
        elif control == "ask":
            events.append({"verb": "clarify", "target": "user", "args": {"reason": "confirmation_required"}})
        else:
            if scope.get("mode") == "redacted":
                events.append({"verb": "redact", "target": focal_id, "args": {"remove": "sensitive_fields"}})
            elif scope.get("mode") in {"summary", "status_only"}:
                events.append({"verb": "summarize", "target": focal_id, "args": {"mode": scope.get("mode")}})
            events.append({"verb": "dispatch", "target": target, "args": {"scope": scope.get("mode")}})
        return events


class NoPlanArchetypeHarness(FinalHarness):
    build_plan_events = LegacyPolicyPlanHarness.build_plan_events
class NoPolicyFromControlHarness(FinalHarness):
    def build_policy(self, task, focal, target, control, scope, evidence):
        policy = super().build_policy(task, focal, target, control, scope, evidence)
        policy["risk_flags"] = [f for f in policy["risk_flags"] if f not in {"clarification_required", "precondition_invalidated", "safety"}]
        policy["violations"] = []
        policy["requires_confirmation"] = bool(scope.get("requires_user_confirmation"))
        return policy
class NoPolicyFromScopeHarness(FinalHarness):
    def build_policy(self, task, focal, target, control, scope, evidence):
        policy = super().build_policy(task, focal, target, control, scope, evidence)
        policy["risk_flags"] = [f for f in policy["risk_flags"] if f not in {"minimal_disclosure", "local_only", "sensitive_content"}]
        return policy
class NoCrossFieldValidatorHarness(FinalHarness):
    def validate_plan_policy_consistency(self, events, focal_id, target, control, scope, policy):
        return events
class NoSummaryPlanHarness(FinalHarness):
    def build_plan_events(self, task, focal_id, target, control, scope, policy):
        if scope.get("mode") == "summary" and control not in {"ask", "hold"}:
            return [{"verb": "read", "target": focal_id, "args": {"purpose": "inspect_context"}}, {"verb": "dispatch", "target": target, "args": {"scope": "summary"}}]
        return super().build_plan_events(task, focal_id, target, control, scope, policy)
class NoRedactionPlanHarness(FinalHarness):
    def build_plan_events(self, task, focal_id, target, control, scope, policy):
        if scope.get("mode") == "redacted" and control not in {"ask", "hold"}:
            return [{"verb": "read", "target": focal_id, "args": {"purpose": "minimal_disclosure"}}, {"verb": "dispatch", "target": target, "args": {"scope": "redacted"}}]
        return super().build_plan_events(task, focal_id, target, control, scope, policy)
class NoHoldGuardPlanHarness(FinalHarness):
    def build_plan_events(self, task, focal_id, target, control, scope, policy):
        if control == "hold":
            return [{"verb": "read", "target": focal_id, "args": {"purpose": "inspect_context"}}]
        return super().build_plan_events(task, focal_id, target, control, scope, policy)


def plan_parts(pred_events: list[dict[str, Any]], exp_events: list[dict[str, Any]]) -> dict[str, float]:
    pred_events = pred_events if isinstance(pred_events, list) else []
    exp_events = exp_events if isinstance(exp_events, list) else []
    pred_verbs = [e.get("verb") for e in pred_events]
    exp_verbs = [e.get("verb") for e in exp_events]
    return {
        "sequence": 1.0 if pred_verbs == exp_verbs else 0.0,
        "count": 1.0 if len(pred_events) == len(exp_events) else 0.0,
        "first": 1.0 if pred_verbs[:1] == exp_verbs[:1] else 0.0,
        "final": 1.0 if pred_verbs[-1:] == exp_verbs[-1:] else 0.0,
        "verb_f1": _f1(set(pred_verbs), set(exp_verbs)),
    }


def evaluate(cls: type[FinalHarness]) -> dict[str, Any]:
    tasks = load_jsonl(data_path("dev_tasks.jsonl"))
    refs = load_json(data_path("dev_answers.json"))["answers"]
    payload, _ = run_harness_with_traces(tasks, cls, harness_name=f"policy_plan_{cls.__name__}")
    validate_payload(payload, {str(t["id"]) for t in tasks})
    metrics = score_dev_submission(payload, {"answers": refs})
    policy_parts = Counter(); policy_totals = Counter(); plan_cftcs = 0; policy_cftcs = 0; cftcs = 0
    plan_parts_sum = Counter(); plan_parts_total = Counter(); exact_policy = exact_plan = 0
    for tid, pred in payload["answers"].items():
        exp = refs[tid]
        ppol, epol = pred["policy"], exp["policy"]
        pplan, eplan = pred["plan_events"], exp["expected_events"]
        policy_score = _policy_score(ppol, epol)
        plan_score = _plan_score(pplan, eplan)
        exact_policy += int(policy_score == 1.0); exact_plan += int(plan_score == 1.0)
        policy_parts["risk_flags"] += _f1(_set(ppol.get("risk_flags")), _set(epol.get("risk_flags"))); policy_totals["risk_flags"] += 1
        policy_parts["violations"] += _f1(_set(ppol.get("violations")), _set(epol.get("violations"))); policy_totals["violations"] += 1
        policy_parts["requires_confirmation"] += int(bool(ppol.get("requires_confirmation")) == bool(epol.get("requires_confirmation"))); policy_totals["requires_confirmation"] += 1
        for k, v in plan_parts(pplan, eplan).items(): plan_parts_sum[k] += v; plan_parts_total[k] += 1
        upstream_ok = pred.get("focal_id") == exp.get("focal_id") and pred.get("target") == exp.get("target") and pred.get("control") == exp.get("control") and pred.get("content_scope") == exp.get("content_scope")
        if upstream_ok:
            cftcs += 1; policy_cftcs += policy_score; plan_cftcs += plan_score
    return {
        "metrics": metrics,
        "exact_policy": exact_policy,
        "exact_plan": exact_plan,
        "policy_parts": {k: round(policy_parts[k] / policy_totals[k], 4) for k in policy_totals},
        "plan_parts": {k: round(plan_parts_sum[k] / plan_parts_total[k], 4) for k in plan_parts_total},
        "policy_at_cftcs": round(policy_cftcs / cftcs, 4) if cftcs else 0.0,
        "plan_at_cftcs": round(plan_cftcs / cftcs, 4) if cftcs else 0.0,
        "payload": payload,
    }


def main() -> None:
    before = evaluate(LegacyPolicyPlanHarness)
    after = evaluate(FinalHarness)
    refs = load_json(data_path("dev_answers.json"))["answers"]
    policy_new_correct = policy_new_wrong = plan_new_correct = plan_new_wrong = 0
    for tid, exp in refs.items():
        before_answer = before["payload"]["answers"][tid]
        after_answer = after["payload"]["answers"][tid]
        before_policy_exact = _policy_score(before_answer["policy"], exp["policy"]) == 1.0
        after_policy_exact = _policy_score(after_answer["policy"], exp["policy"]) == 1.0
        before_plan_exact = _plan_score(before_answer["plan_events"], exp["expected_events"]) == 1.0
        after_plan_exact = _plan_score(after_answer["plan_events"], exp["expected_events"]) == 1.0
        policy_new_correct += int(after_policy_exact and not before_policy_exact)
        policy_new_wrong += int(before_policy_exact and not after_policy_exact)
        plan_new_correct += int(after_plan_exact and not before_plan_exact)
        plan_new_wrong += int(before_plan_exact and not after_plan_exact)
    variants = {
        "full": after,
        "no_plan_archetype_table": evaluate(NoPlanArchetypeHarness),
        "no_policy_from_control": evaluate(NoPolicyFromControlHarness),
        "no_policy_from_scope": evaluate(NoPolicyFromScopeHarness),
        "no_cross_field_validator": evaluate(NoCrossFieldValidatorHarness),
        "no_summary_plan": evaluate(NoSummaryPlanHarness),
        "no_redaction_plan": evaluate(NoRedactionPlanHarness),
        "no_hold_guard_plan": evaluate(NoHoldGuardPlanHarness),
    }
    rows = []
    for name, result in variants.items():
        m = result["metrics"]
        rows.append(f"| {name} | {m['overall']:.4f} | {m['axes']['policy']:.4f} | {m['axes']['plan']:.4f} | {m['axes']['control']:.4f} | {m['axes']['content_scope']:.4f} | {result['policy_at_cftcs']:.4f} | {result['plan_at_cftcs']:.4f} |")
    lines = [
        "# Policy / Plan Implementation Summary", "",
        "This compact report contains aggregate metrics only; no task-level prediction or trace dumps are committed.", "",
        "## Schema Summary", "",
        "- `policy` requires `risk_flags`, `violations`, and `requires_confirmation`.",
        "- `plan_events` is a list of objects with `verb`, `target`, and `args`.",
        "- Dev references score plans against `expected_events`; observed archetypes are `read→verify→update`, `read→redact→dispatch`, `read→clarify`, `read→guard`, `read→dispatch`, and `read→summarize→dispatch`.", "",
        "## Before / After", "",
        f"- Overall: {before['metrics']['overall']:.4f} -> {after['metrics']['overall']:.4f}",
        f"- Focal: {before['metrics']['axes']['focal']:.4f} -> {after['metrics']['axes']['focal']:.4f}",
        f"- Target: {before['metrics']['axes']['target']:.4f} -> {after['metrics']['axes']['target']:.4f}",
        f"- Control: {before['metrics']['axes']['control']:.4f} -> {after['metrics']['axes']['control']:.4f}",
        f"- Content Scope: {before['metrics']['axes']['content_scope']:.4f} -> {after['metrics']['axes']['content_scope']:.4f}",
        f"- Policy: {before['metrics']['axes']['policy']:.4f} -> {after['metrics']['axes']['policy']:.4f}",
        f"- Plan: {before['metrics']['axes']['plan']:.4f} -> {after['metrics']['axes']['plan']:.4f}",
        f"- Policy@Correct Focal+Target+Control+ContentScope: {before['policy_at_cftcs']:.4f} -> {after['policy_at_cftcs']:.4f}",
        f"- Plan@Correct Focal+Target+Control+ContentScope: {before['plan_at_cftcs']:.4f} -> {after['plan_at_cftcs']:.4f}", "",
        f"- Exact policy count: {before['exact_policy']} -> {after['exact_policy']} (newly correct {policy_new_correct}, newly wrong {policy_new_wrong})",
        f"- Exact plan count: {before['exact_plan']} -> {after['exact_plan']} (newly correct {plan_new_correct}, newly wrong {plan_new_wrong})", "",
        "## Policy Component Accuracy After", "",
        *[f"- {k}: {v:.4f}" for k, v in after["policy_parts"].items()], "",
        "## Plan Component Accuracy After", "",
        *[f"- {k}: {v:.4f}" for k, v in after["plan_parts"].items()], "",
        "## Ablation", "",
        "| Variant | Overall | Policy | Plan | Control | Content Scope | Policy@CFTCS | Plan@CFTCS |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        *rows, "",
        "## Remaining Failure Types", "",
        "- Policy risk flags still underfit some target/precondition combinations because the builder uses runtime records rather than task-specific labels.",
        "- Plan exactness is still limited by upstream content_scope/control errors and by nuanced `remove=raw_quote` versus `remove=sensitive_fields` boundaries.",
    ]
    Path("reports/policy_plan_implementation_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
