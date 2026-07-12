from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import FinalHarness, run_harness_with_traces, score_dev_submission, validate_payload
from data_utils import load_json, load_jsonl, data_path

class NoStructuredChainHarness(FinalHarness):
    enable_focal_structured_chain = False

class NoDirectRecordHarness(FinalHarness):
    enable_focal_direct_record = False

class NoHistoryRefHarness(FinalHarness):
    enable_focal_history_ref = False

class NoPromptOverlapHarness(FinalHarness):
    enable_focal_prompt_overlap = False

VARIANTS = {
    'full': FinalHarness,
    'no_structured_chain': NoStructuredChainHarness,
    'no_direct_record': NoDirectRecordHarness,
    'no_history_ref': NoHistoryRefHarness,
    'no_prompt_overlap': NoPromptOverlapHarness,
}

def evaluate_variant(harness_cls: type[FinalHarness]) -> dict:
    tasks = load_jsonl(data_path('dev_tasks.jsonl'))
    refs = load_json(data_path('dev_answers.json'))
    payload, traces = run_harness_with_traces(tasks, harness_cls, harness_name=f'focal_{harness_cls.__name__}')
    validate_payload(payload, {str(t['id']) for t in tasks})
    metrics = score_dev_submission(payload, refs)
    correct = sum(1 for tid, pred in payload['answers'].items() if pred.get('focal_id') == refs['answers'][tid].get('focal_id'))
    return {'metrics': metrics, 'focal_correct': correct, 'focal_wrong': len(tasks) - correct}

def main():
    rows = {name: evaluate_variant(cls) for name, cls in VARIANTS.items()}
    lines = ['# Focal Resolver Ablation', '', '| Variant | Overall | Focal | Correct | Wrong |', '| --- | ---: | ---: | ---: | ---: |']
    for name, row in rows.items():
        lines.append(f"| {name} | {row['metrics']['overall']:.4f} | {row['metrics']['axes']['focal']:.4f} | {row['focal_correct']} | {row['focal_wrong']} |")
    lines += ['', '## Interpretation', '- `no_structured_chain` isolates the contribution of the phase → marker → ref_code → object resolver.', '- `no_direct_record`, `no_history_ref`, and `no_prompt_overlap` check whether fallback families are carrying meaningful examples or mainly preserving safety.', '- The full resolver keeps explicit fallback behavior so malformed chains do not abort a run.']
    Path('reports/focal_ablation.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('\n'.join(lines))
if __name__ == '__main__':
    main()
