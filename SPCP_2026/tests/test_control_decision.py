from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import FinalHarness


def base_task(records, prompt='send summary', attrs=None):
    return {
        'id': 'synthetic', 'session_id': 's', 'turn_index': 1,
        'prompt': prompt, 'visible_history': [], 'personal_memory': [],
        'device_state': {'objects': [{'id': 'obj_content', 'type': 'message', 'attrs': attrs if attrs is not None else {'recipient': 'project_room'}}], 'records': records},
        'available_actions': []
    }


def answer(task):
    h=FinalHarness(); ans=h.answer_task(task, {})
    return ans, h.last_decision_trace['control']


def test_safe_execution_without_unresolved_constraints_proceeds():
    ans, trace = answer(base_task([{'type': 'resolved_target', 'value': 'project_room'}]))
    assert ans['control'] == 'proceed'
    assert trace['selected_by'] == 'C-06_execute_as_resolved'


def test_removable_sensitive_fields_choose_amend():
    task=base_task([{'type':'resolved_target','value':'audit_vendor'}, {'type':'external_share_policy','value':'raw_quote_forbidden'}], attrs={'contains':['summary','raw_quote'], 'recipient':'audit_vendor'})
    ans, trace = answer(task)
    assert ans['control'] == 'amend'
    assert trace['selected_by'] == 'C-05_safe_automatic_amendment'


def test_unresolved_user_choice_chooses_ask():
    task=base_task([{'type':'resolved_target','value':'audit_vendor'}, {'type':'ambiguous_focal','value':'multiple_focal_candidates_present'}, {'type':'route_candidate_snapshot','value':'external_candidates_present'}, {'type':'dispatch_authority_check','value':'authority_incomplete'}, {'type':'share_boundary_update','value':'dispatch_blocked_until_binding'}])
    ans, trace = answer(task)
    assert ans['control'] == 'ask'
    assert trace['selected_by'] == 'C-04_unresolved_user_choice'


def test_non_resolvable_blocking_condition_chooses_hold():
    task=base_task([{'type':'resolved_target','value':'fitness_coach'}, {'type':'external_share_policy','value':'doctor_note_forbidden'}], prompt='오늘 건강 기록을 공유해줘')
    ans, trace = answer(task)
    assert ans['control'] == 'hold'
    assert trace['selected_by'] == 'C-03_non_resolvable_block_or_violation'


def test_resolved_target_ambiguity_does_not_force_ask():
    task=base_task([{'type':'resolved_target','value':'project_room'}, {'type':'ambiguous_target','value':'surface_recipient_and_resolved_target_both_recent'}, {'type':'dispatch_authority_check','value':'internal_binding_confirmed'}, {'type':'share_boundary_update','value':'redacted_external_boundary'}])
    ans, trace = answer(task)
    assert ans['control'] == 'proceed'
    assert trace['selected_by'] == 'C-06_execute_as_resolved'


def test_newer_local_update_supersedes_old_external_confirmation():
    task=base_task([{'type':'resolved_target','value':'project_room'}, {'type':'ambiguous_target','value':'surface_recipient_and_resolved_target_both_recent'}, {'type':'external_share_policy','value':'raw_quote_forbidden'}], prompt='공유하지 말고 기기 내부 상태 업데이트로 끝내줘')
    ans, trace = answer(task)
    assert ans['target'] == 'memory_store'
    assert ans['control'] == 'proceed'
    assert trace['selected_by'] == 'C-01_local_update_proceeds'


def test_fixed_slm_confirmation_signal_alone_does_not_force_ask():
    task=base_task([{'type':'resolved_target','value':'project_room'}], prompt='확인 필요성이라는 단어가 있지만 현재 route는 확정되어 있다')
    ans, trace = answer(task)
    assert ans['control'] == 'proceed'


def test_previous_consent_is_not_reused_after_scope_expansion():
    task=base_task([{'type':'resolved_target','value':'project_room'}, {'type':'consent','value':'revoked'}], prompt='이전 동의가 있어도 이번에는 외부로 보내줘')
    ans, trace = answer(task)
    assert ans['control'] == 'hold'
    assert trace['selected_by'] == 'C-03_non_resolvable_block_or_violation'
