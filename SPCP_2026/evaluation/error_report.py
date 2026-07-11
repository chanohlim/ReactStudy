from __future__ import annotations
import json, sys, collections
from pathlib import Path

def classify(row):
    fc=row['field_correct']; pred=row['prediction']; exp=row['expected']; out=[]
    if not fc['focal_id']: out.append('focal resolution failure')
    if fc['focal_id'] and not fc['target']: out.append('target resolution failure')
    if fc['focal_id'] and not fc['control']: out.append('control classification failure')
    if fc['target'] and fc['control'] and not fc['content_scope']: out.append('content scope failure')
    if fc['target'] and fc['control'] and not fc['policy']: out.append('policy inconsistency')
    if pred.get('plan_events') != exp.get('expected_events'): out.append('plan construction failure')
    if not out: out.append('cross-field inconsistency')
    return out

def main(path='reports/runs/run_001.json'):
    run=json.loads(Path(path).read_text(encoding='utf-8')); counts=collections.Counter(); examples=collections.defaultdict(list)
    for row in run['tasks']:
        if row['all_core_correct']: continue
        for c in classify(row):
            counts[c]+=1
            if len(examples[c])<3: examples[c].append(row['task_id'])
    lines=['# Baseline Error Analysis','',f"Run: `{path}`",'', '## Failure type counts','']
    for k,v in counts.most_common(): lines.append(f'- {k}: {v} (examples: {", ".join(examples[k])})')
    lines += ['', '## General improvement candidates', '- 최신 record와 session update의 우선순위를 명시하는 precedence rule 연구.', '- focal/target/control의 의존 관계를 trace로 검증하는 consistency checker 추가.', '- plan_events를 공식 action ontology에 더 안정적으로 매핑하는 일반 builder 개선.']
    Path('reports/baseline_error_analysis.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('\n'.join(lines))
if __name__=='__main__': main(sys.argv[1] if len(sys.argv)>1 else 'reports/runs/run_001.json')
