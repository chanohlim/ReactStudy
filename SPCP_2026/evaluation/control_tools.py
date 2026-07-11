from __future__ import annotations
import json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import FinalHarness, run_harness_with_traces, score_dev_submission, validate_payload
from data_utils import load_json, load_jsonl, data_path

class NoLocalPrecedenceHarness(FinalHarness):
    enable_control_local_precedence = False
class NoSafeAmendHarness(FinalHarness):
    enable_control_safe_amend = False
class NoUserChoiceHarness(FinalHarness):
    enable_control_user_choice = False
class NoBlockingHarness(FinalHarness):
    enable_control_blocking = False
class NoFixedSLMHarness(FinalHarness):
    enable_control_fixed_slm = False

VARIANTS = {
    'full': FinalHarness,
    'no_local_precedence': NoLocalPrecedenceHarness,
    'no_safe_amend': NoSafeAmendHarness,
    'no_user_choice': NoUserChoiceHarness,
    'no_blocking': NoBlockingHarness,
    'no_fixed_slm_evidence': NoFixedSLMHarness,
}

def summarize(payload: dict, refs: dict) -> dict:
    answers = payload['answers']; ref_answers = refs['answers']
    control_correct = 0; ft = 0; ft_control = 0; cm = Counter()
    for tid, pred in answers.items():
        exp = ref_answers[tid]
        c_ok = pred.get('control') == exp.get('control')
        control_correct += int(c_ok)
        ft_ok = pred.get('focal_id') == exp.get('focal_id') and pred.get('target') == exp.get('target')
        if ft_ok:
            ft += 1; ft_control += int(c_ok); cm[(exp.get('control'), pred.get('control'))] += 1
    return {'control_correct': control_correct, 'control_wrong': len(answers)-control_correct, 'control_at_correct_focal_target': ft_control / ft if ft else 0.0, 'confusion': dict(cm)}

def evaluate_variant(cls: type[FinalHarness]) -> dict:
    tasks=load_jsonl(data_path('dev_tasks.jsonl')); refs=load_json(data_path('dev_answers.json'))
    payload,_=run_harness_with_traces(tasks, cls, harness_name=f'control_{cls.__name__}')
    validate_payload(payload, {str(t['id']) for t in tasks})
    metrics=score_dev_submission(payload, refs)
    row=summarize(payload, refs); row['metrics']=metrics
    return row

def main():
    rows={name:evaluate_variant(cls) for name,cls in VARIANTS.items()}
    lines=['# Control Ablation', '', '| Variant | Overall | Focal | Target | Control | Control Correct | Control@Focal+Target |', '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for name,row in rows.items():
        m=row['metrics']; axes=m['axes']
        lines.append(f"| {name} | {m['overall']:.4f} | {axes['focal']:.4f} | {axes['target']:.4f} | {axes['control']:.4f} | {row['control_correct']} | {row['control_at_correct_focal_target']:.4f} |")
    lines += ['', '## Interpretation', '- `no_local_precedence` isolates local/internal update superseding older ambiguity, security, consent, and external-redaction signals.', '- `no_safe_amend` measures automatic scope-narrowing/redaction feasibility.', '- `no_user_choice` measures unresolved user decision and target/precondition ambiguity handling.', '- `no_blocking` measures non-resolvable safety/policy blocking.', '- `no_fixed_slm_evidence` confirms FixedSLM is auxiliary and not an oracle.']
    Path('reports/control_ablation.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('\n'.join(lines))
if __name__=='__main__': main()
