from __future__ import annotations
from pathlib import Path
from harness import FinalHarness, run_harness, validate_payload, write_submission_csv
from data_utils import load_jsonl, data_path

def main():
    tasks=load_jsonl(data_path('screening_tasks.jsonl'))
    payload=run_harness(tasks, FinalHarness, harness_name='python_baseline_screening')
    validate_payload(payload, {str(t['id']) for t in tasks})
    write_submission_csv(payload, Path('submission.csv'))
    print('wrote submission.csv')
if __name__=='__main__': main()
