from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import FinalHarness


def _answer(task):
    return FinalHarness().answer_task(task, {})


def test_latest_phase_resolves_marker_then_ref_then_object():
    task = {
        'id': 'synthetic_phase_chain', 'prompt': 'latest object please', 'visible_history': [], 'personal_memory': [],
        'device_state': {
            'objects': [
                {'id': 'obj_old', 'type': 'message', 'attrs': {'ref_code': 'WM-OLD', 'body': 'latest object please'}},
                {'id': 'obj_new', 'type': 'file', 'attrs': {'ref_code': 'WM-NEW', 'title': 'authoritative source'}},
            ],
            'records': [
                {'type': 'route_binding_order', 'value': 'boundary_after_authority'},
                {'type': 'focal_marker_refs', 'value': {'marker_to_ref': {'marker_alpha': 'WM-NEW', 'marker_beta': 'WM-OLD'}}},
                {'type': 'focal_resolution_trace', 'value': {'latest_phase': 'boundary', 'phase_to_marker': {'boundary': 'marker_alpha', 'authority': 'marker_beta'}}},
            ],
        },
    }
    answer = _answer(task)
    assert answer['focal_id'] == 'obj_new'


def test_missing_marker_chain_falls_back_safely_to_history_ref():
    task = {
        'id': 'synthetic_missing_chain', 'prompt': 'handle the prior item', 'visible_history': [{'summary': 'previously selected WM-HIST'}], 'personal_memory': [],
        'device_state': {
            'objects': [
                {'id': 'obj_hist', 'type': 'file', 'attrs': {'ref_code': 'WM-HIST', 'title': 'prior source'}},
                {'id': 'obj_other', 'type': 'message', 'attrs': {'ref_code': 'WM-OTHER', 'body': 'handle the prior item'}},
            ],
            'records': [
                {'type': 'focal_marker_refs', 'value': {'marker_to_ref': {'marker_alpha': 'WM-MISSING'}}},
                {'type': 'focal_resolution_trace', 'value': {'latest_phase': 'boundary', 'phase_to_marker': {'boundary': 'marker_alpha'}}},
            ],
        },
    }
    answer = _answer(task)
    assert answer['focal_id'] == 'obj_hist'


def test_target_like_surface_object_does_not_override_structured_content_focal():
    task = {
        'id': 'synthetic_target_surface', 'prompt': 'send it to minji', 'visible_history': [], 'personal_memory': [],
        'device_state': {
            'objects': [
                {'id': 'obj_message', 'type': 'message', 'attrs': {'ref_code': 'WM-MSG', 'recipient': 'minji', 'body': 'send it to minji'}},
                {'id': 'obj_file', 'type': 'file', 'attrs': {'ref_code': 'WM-FILE', 'title': 'source content'}},
            ],
            'records': [
                {'type': 'focal_marker_refs', 'value': {'marker_to_ref': {'marker_alpha': 'WM-FILE'}}},
                {'type': 'focal_resolution_trace', 'value': {'latest_phase': 'boundary', 'phase_to_marker': {'boundary': 'marker_alpha'}}},
                {'type': 'resolved_target', 'value': 'minji'},
            ],
        },
    }
    answer = _answer(task)
    assert answer['focal_id'] == 'obj_file'


def test_newer_structured_reference_overrides_stale_history():
    task = {
        'id': 'synthetic_newer_over_stale', 'prompt': 'use the latest resolved source', 'visible_history': [{'summary': 'old source WM-OLD'}], 'personal_memory': [],
        'device_state': {
            'objects': [
                {'id': 'obj_old', 'type': 'file', 'attrs': {'ref_code': 'WM-OLD', 'title': 'old source'}},
                {'id': 'obj_new', 'type': 'file', 'attrs': {'ref_code': 'WM-NEW', 'title': 'latest source'}},
            ],
            'records': [
                {'type': 'focal_marker_refs', 'value': {'marker_to_ref': {'marker_alpha': 'WM-NEW'}}},
                {'type': 'focal_resolution_trace', 'value': {'latest_phase': 'boundary', 'phase_to_marker': {'boundary': 'marker_alpha'}}},
            ],
        },
    }
    answer = _answer(task)
    assert answer['focal_id'] == 'obj_new'
