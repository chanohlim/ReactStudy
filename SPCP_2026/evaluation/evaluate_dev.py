from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness import score_dev_submission, validate_payload
from data_utils import load_json, load_jsonl, data_path

def evaluate(payload):
    answers = load_json(data_path('dev_answers.json'))
    validate_payload(payload, {str(t['id']) for t in load_jsonl(data_path('dev_tasks.jsonl'))})
    return score_dev_submission(payload, answers)

if __name__ == '__main__':
    payload=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    print(json.dumps(evaluate(payload), ensure_ascii=False, indent=2))
