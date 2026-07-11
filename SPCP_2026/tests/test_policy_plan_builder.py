from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import FinalHarness


def harness_with_traces(target: str = "project_room") -> FinalHarness:
    h = FinalHarness()
    h.last_target_trace = {"selected": target, "selected_category": "channel"}
    h.last_control_trace = {"context": {}}
    return h


def task(records=None):
    return {"id": "synthetic", "prompt": "", "device_state": {"objects": [], "records": records or []}}


def focal():
    return {"id": "obj_content", "type": "note", "attrs": {"contains": ["summary", "raw_quote"]}}


def verbs(events):
    return [event["verb"] for event in events]


def test_status_only_proceed_builds_verify_update_plan():
    h = harness_with_traces("memory_store")
    scope = {"mode": "status_only", "allowed_fields": ["status"], "excluded_fields": ["raw_quote"], "requires_user_confirmation": False}
    policy = h.build_policy(task([{"type": "persistent_memory_write", "value": "x"}]), focal(), "memory_store", "proceed", scope, {})
    events = h.build_plan_events(task(), "obj_content", "memory_store", "proceed", scope, policy)
    assert verbs(events) == ["read", "verify", "update"]
    assert events[1]["target"] == "share_boundary_update"


def test_redacted_amend_builds_redact_dispatch_plan():
    h = harness_with_traces()
    scope = {"mode": "redacted", "allowed_fields": ["summary"], "excluded_fields": ["raw_quote"], "requires_user_confirmation": False}
    policy = h.build_policy(task(), focal(), "project_room", "amend", scope, {})
    events = h.build_plan_events(task(), "obj_content", "project_room", "amend", scope, policy)
    assert verbs(events) == ["read", "redact", "dispatch"]
    assert events[1]["args"]["remove"] == "raw_quote"


def test_summary_scope_builds_summarize_dispatch_plan():
    h = harness_with_traces()
    scope = {"mode": "summary", "allowed_fields": ["summary"], "excluded_fields": ["raw_quote"], "requires_user_confirmation": False}
    policy = h.build_policy(task(), focal(), "project_room", "proceed", scope, {})
    events = h.build_plan_events(task(), "obj_content", "project_room", "proceed", scope, policy)
    assert verbs(events) == ["read", "summarize", "dispatch"]


def test_ask_builds_clarify_plan_without_dispatch():
    h = harness_with_traces("user")
    scope = {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": True}
    policy = h.build_policy(task(), focal(), "user", "ask", scope, {})
    events = h.build_plan_events(task(), "obj_content", "user", "ask", scope, policy)
    assert verbs(events) == ["read", "clarify"]
    assert "dispatch" not in verbs(events)
    assert policy["requires_confirmation"] is True


def test_hold_builds_guard_plan_without_dispatch():
    h = harness_with_traces()
    scope = {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": False}
    policy = h.build_policy(task(), focal(), "project_room", "hold", scope, {})
    events = h.build_plan_events(task(), "obj_content", "project_room", "hold", scope, policy)
    assert verbs(events) == ["read", "guard"]
    assert "dispatch" not in verbs(events)
    assert policy["requires_confirmation"] is False


def test_raw_proceed_does_not_include_redact_or_summarize():
    h = harness_with_traces()
    scope = {"mode": "raw", "allowed_fields": ["summary"], "excluded_fields": [], "requires_user_confirmation": False}
    policy = h.build_policy(task(), focal(), "project_room", "proceed", scope, {})
    events = h.build_plan_events(task(), "obj_content", "project_room", "proceed", scope, policy)
    assert verbs(events) == ["read", "dispatch"]
    assert "redact" not in verbs(events)
    assert "summarize" not in verbs(events)


def test_policy_redaction_applied_when_excluded_fields_present():
    h = harness_with_traces()
    scope = {"mode": "redacted", "allowed_fields": ["summary"], "excluded_fields": ["raw_quote"], "requires_user_confirmation": False}
    policy = h.build_policy(task(), focal(), "project_room", "amend", scope, {})
    assert "minimal_disclosure" in policy["risk_flags"]
    assert policy["requires_confirmation"] is False


def test_policy_confirmation_not_equal_to_control_ask_blindly():
    h = harness_with_traces()
    scope = {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": False}
    policy = h.build_policy(task(), focal(), "project_room", "hold", scope, {})
    assert policy["requires_confirmation"] is False


def test_cross_field_validator_removes_dispatch_from_hold():
    h = harness_with_traces()
    bad_events = [{"verb": "read", "target": "obj_content", "args": {}}, {"verb": "dispatch", "target": "project_room", "args": {"scope": "raw"}}]
    scope = {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": False}
    policy = {"risk_flags": ["safety"], "violations": ["precondition_changed_ignored"], "requires_confirmation": False}
    repaired = h.validate_plan_policy_consistency(bad_events, "obj_content", "project_room", "hold", scope, policy)
    assert verbs(repaired) == ["read", "guard"]
