from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import run_harness, run_harness_with_traces


class MemoryProbeHarness:
    prepare_calls = 0
    seen_at_prepare = None

    def __init__(self):
        self.sequence = []

    def prepare(self, tasks):
        type(self).prepare_calls += 1
        type(self).seen_at_prepare = list(tasks)

    def answer_task(self, task, session):
        session.setdefault("seen", []).append(task["id"])
        self.sequence.append(task["id"])
        return {
            "focal_id": task["id"],
            "target": session.get("seen", [""])[0],
            "control": "proceed",
            "content_scope": {"mode": "raw", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": False},
            "policy": {"risk_flags": [], "violations": [], "requires_confirmation": False},
            "plan_events": [],
        }


def task(tid, session_id, turn_index):
    return {"id": tid, "session_id": session_id, "turn_index": turn_index, "device_state": {"objects": [], "records": []}}


def test_same_session_preserves_memory():
    payload = run_harness([task("b", "s1", 2), task("a", "s1", 1)], MemoryProbeHarness)
    assert payload["answers"]["a"]["target"] == "a"
    assert payload["answers"]["b"]["target"] == "a"


def test_different_sessions_do_not_share_memory():
    payload = run_harness([task("a", "s1", 1), task("b", "s2", 1)], MemoryProbeHarness)
    assert payload["answers"]["a"]["target"] == "a"
    assert payload["answers"]["b"]["target"] == "b"


def test_task_order_is_sorted_within_session():
    payload = run_harness([task("b", "s1", 2), task("a", "s1", 1)], MemoryProbeHarness)
    assert list(payload["answers"].keys()) == ["a", "b"]


def test_new_run_starts_with_clean_session_state():
    payload1 = run_harness([task("a", "s1", 1)], MemoryProbeHarness)
    payload2 = run_harness([task("b", "s1", 1)], MemoryProbeHarness)
    assert payload1["answers"]["a"]["target"] == "a"
    assert payload2["answers"]["b"]["target"] == "b"


def test_run_dev_and_screening_runner_use_same_lifecycle():
    tasks = [task("b", "s1", 2), task("a", "s1", 1), task("c", "s2", 1)]
    payload = run_harness(tasks, MemoryProbeHarness)
    payload_with_traces, traces = run_harness_with_traces(tasks, MemoryProbeHarness)
    assert payload["answers"] == payload_with_traces["answers"]
    assert set(traces) == {"a", "b", "c"}
