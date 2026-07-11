from __future__ import annotations
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import validate_payload, write_submission_csv


def test_submission_json_csv_roundtrip(tmp_path: Path):
    payload={
        'schema':'scpc.final.answer.v1',
        'meta':{'uses_external_api':False,'fixed_slm_policy':'local_fixed_slm_only','model_id':'scpc-final-fixed-slm-local-facade'},
        'answers':{'task_x':{'focal_id':'obj_x','target':'user','control':'ask','content_scope':{'mode':'summary','allowed_fields':['status'],'excluded_fields':[],'requires_user_confirmation':True},'policy':{'risk_flags':[],'violations':[],'requires_confirmation':True},'plan_events':[{'verb':'clarify','target':'user','args':{'reason':'confirmation_required'}}]}}
    }
    validate_payload(payload, {'task_x'})
    raw=json.loads(json.dumps(payload, ensure_ascii=False))
    assert raw == payload
    p=tmp_path/'submission.csv'; write_submission_csv(payload,p)
    with p.open(encoding='utf-8', newline='') as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==1 and set(rows[0])=={'submission'}
    restored=json.loads(rows[0]['submission'])
    assert restored==payload


def test_invalid_control_rejected():
    payload={'schema':'scpc.final.answer.v1','meta':{'uses_external_api':False,'fixed_slm_policy':'local_fixed_slm_only','model_id':'scpc-final-fixed-slm-local-facade'},'answers':{'task_x':{'focal_id':'obj','target':'user','control':'bad','content_scope':{'mode':'none','allowed_fields':[],'excluded_fields':[],'requires_user_confirmation':False},'policy':{'risk_flags':[],'violations':[],'requires_confirmation':False},'plan_events':[]}}}
    try:
        validate_payload(payload, {'task_x'})
    except ValueError as e:
        assert 'invalid control' in str(e)
    else:
        raise AssertionError('invalid control was accepted')
