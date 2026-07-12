from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import FinalHarness


def make_harness(target: str = "project_room", **control_context):
    h = FinalHarness()
    h.last_target_trace = {"selected": target, "selected_category": "channel"}
    base_context = {
        "local_update_requested": False,
        "external_dispatch_requested": target not in {"user", "memory_store"},
        "dispatch_cancelled": False,
        "action_blocked": False,
        "user_choice_required": False,
        "confirmation_signal": False,
    }
    base_context.update(control_context)
    h.last_control_trace = {"context": base_context}
    return h


def task(records=None, prompt=""):
    return {"id": "synthetic", "prompt": prompt, "device_state": {"objects": [], "records": records or []}}


def focal(contains=None):
    return {"id": "obj_content", "type": "note", "attrs": {"contains": contains or ["summary", "title"]}}


def test_local_internal_update_uses_status_only_scope():
    h = make_harness(target="memory_store", local_update_requested=True, external_dispatch_requested=False)
    scope = h.build_content_scope(task(records=[{"type": "persistent_memory_write", "value": {"memory_key": "x"}}]), focal(["summary", "raw_quote"]), "proceed", {})
    assert scope["mode"] == "status_only"
    assert scope["allowed_fields"] == ["status"]
    assert scope["requires_user_confirmation"] is False
    assert h.last_content_scope_trace["selected_by"] == "S-02_local_status_only"


def test_safe_redaction_builds_redacted_scope():
    h = make_harness(target="project_room", external_dispatch_requested=True)
    scope = h.build_content_scope(task(), focal(["summary", "title", "location", "raw_quote"]), "amend", {"requires_redaction": True})
    assert scope["mode"] == "redacted"
    assert "location" in scope["excluded_fields"]
    assert "raw_quote" in scope["excluded_fields"]
    assert scope["requires_user_confirmation"] is False


def test_hold_uses_none_scope():
    h = make_harness(action_blocked=True)
    scope = h.build_content_scope(task(), focal(["summary", "raw_quote"]), "hold", {})
    assert scope == {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": False}


def test_ask_requires_confirmation_without_dispatch_scope():
    h = make_harness(user_choice_required=True, confirmation_signal=True)
    scope = h.build_content_scope(task(), focal(["summary", "location"]), "ask", {})
    assert scope["mode"] == "none"
    assert scope["allowed_fields"] == []
    assert scope["requires_user_confirmation"] is True


def test_summary_request_uses_summary_scope():
    h = make_harness(target="project_room", external_dispatch_requested=True)
    scope = h.build_content_scope(task(prompt="요약해서 공유해줘"), focal(["summary", "title", "raw_quote"]), "proceed", {})
    assert scope["mode"] == "summary"
    assert "summary" in scope["allowed_fields"]
    assert "raw_quote" in scope["excluded_fields"]


def test_raw_scope_when_no_restrictions_apply():
    h = make_harness(target="project_room", external_dispatch_requested=True)
    scope = h.build_content_scope(task(), focal(["summary", "title"]), "proceed", {})
    assert scope["mode"] == "raw"
    assert scope["excluded_fields"] == []
    assert scope["requires_user_confirmation"] is False


def test_excluded_fields_include_removable_sensitive_fields():
    h = make_harness(target="project_room", external_dispatch_requested=True)
    scope = h.build_content_scope(task(), focal(["summary", "identifier", "payment"]), "amend", {"requires_redaction": True})
    assert scope["mode"] == "redacted"
    assert set(scope["excluded_fields"]) >= {"identifier", "payment"}


def test_redacted_scope_requires_actual_exclusion():
    h = make_harness(target="project_room", external_dispatch_requested=True)
    scope = h.build_content_scope(task(), focal(["summary", "title"]), "amend", {})
    assert scope["mode"] != "redacted"
    assert h.last_content_scope_trace["selected_by"] != "S-04_redacted_amendment"
