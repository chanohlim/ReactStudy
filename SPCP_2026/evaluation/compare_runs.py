from __future__ import annotations
import json, sys
from pathlib import Path

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def changed_fields(a,b):
    fields=['focal_id','target','control','content_scope','policy','plan_events']
    return [f for f in fields if a.get(f)!=b.get(f)]
def main(a,b):
    r1,r2=load(a),load(b); m1,m2=r1['metrics'],r2['metrics']
    def val(m,k): return m.get(k,m.get('axes',{}).get(k,0))
    for k in ['overall','focal','target','control','content_scope','policy','plan']:
        print(f'{k}: {val(m1,k):.4f} -> {val(m2,k):.4f}')
    t1={x['task_id']:x for x in r1['tasks']}; t2={x['task_id']:x for x in r2['tasks']}
    groups={'newly_correct':[],'newly_wrong':[],'still_correct':[],'still_wrong':[]}
    for tid,x in t2.items():
        old=t1.get(tid); 
        if not old: continue
        oc, nc=old['all_core_correct'], x['all_core_correct']
        key='newly_correct' if (not oc and nc) else 'newly_wrong' if (oc and not nc) else 'still_correct' if nc else 'still_wrong'
        groups[key].append({'task_id':tid,'expected':x['expected'],'previous':old['prediction'],'new':x['prediction'],'changed_fields':changed_fields(old['prediction'],x['prediction'])})
    print('Newly Correct:',len(groups['newly_correct'])); print('Newly Wrong:',len(groups['newly_wrong'])); print('Unchanged:',len(groups['still_correct'])+len(groups['still_wrong']))
    out=Path('reports')/f"compare_{Path(a).stem}_vs_{Path(b).stem}.json"; out.write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf-8'); print('Details:',out)
if __name__=='__main__': main(sys.argv[1], sys.argv[2])
