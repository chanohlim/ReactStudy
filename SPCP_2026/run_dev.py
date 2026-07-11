from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from harness import FinalHarness, run_harness_with_traces, score_dev_submission, validate_payload
from data_utils import load_json, load_jsonl, data_path

REPORTS = Path('reports'); RUNS = REPORTS/'runs'

def field_status(pred, exp):
    return {k: pred.get(k)==exp.get(k) for k in ['focal_id','target','control','content_scope','policy']}

def main():
    tasks=load_jsonl(data_path('dev_tasks.jsonl'))
    refs=load_json(data_path('dev_answers.json'))
    payload,traces=run_harness_with_traces(tasks, FinalHarness, harness_name='python_baseline_dev')
    validate_payload(payload, {str(t['id']) for t in tasks})
    metrics=score_dev_submission(payload, refs)
    RUNS.mkdir(parents=True, exist_ok=True)
    n=len(list(RUNS.glob('run_*.json')))+1
    per=[]
    for t in tasks:
        tid=str(t['id']); pred=payload['answers'][tid]; exp=refs['answers'][tid]
        per.append({'task_id':tid,'session_id':t.get('session_id'),'turn_index':t.get('turn_index'), 'prediction':pred,'expected':exp,'field_correct':field_status(pred, exp), 'all_core_correct': all(field_status(pred, exp).values()), 'decision_trace': traces.get(tid)})
    run={'created_at':datetime.now(timezone.utc).isoformat(),'metrics':metrics,'payload_meta':payload['meta'],'tasks':per}
    path=RUNS/f'run_{n:03d}.json'; path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding='utf-8')
    (REPORTS/'baseline_metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding='utf-8')
    labels={'overall':'Overall','focal':'Focal','target':'Target','control':'Control','content_scope':'Content Scope','policy':'Policy','plan':'Plan'}
    
    for k,l in labels.items():
        v = metrics.get(k, metrics.get('axes', {}).get(k, 0.0))
        print(f'{l}: {v:.4f}')
    print('Run file:', path)
if __name__=='__main__': main()
