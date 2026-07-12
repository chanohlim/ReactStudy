# Pipeline Parity Audit

This report contains aggregate pipeline and structure checks only; no task-level prediction or trace dumps are committed.

## Dev Runner vs Screening-Style Dev Runner

- run_dev-style overall: 0.6458
- screening-style-dev overall: 0.6458
- focal: 0.8833 -> 0.8833
- target: 0.8000 -> 0.8000
- control: 0.7000 -> 0.7000
- content_scope: 0.5008 -> 0.5008
- policy: 0.5532 -> 0.5532
- plan: 0.5986 -> 0.5986
- answer count: 120 -> 120
- task id sets equal: true
- identical answer dicts: 120
- different answer dicts: 0

## Alignment Invariants

- task_count: 700
- answer_count: 700
- unique_task_ids: 700
- unique_answer_ids: 700
- missing_count: 0
- unexpected_count: 0
- sets_equal: True
- duplicate_input_ids: 0
- duplicate_answer_ids: 0
- answer_order_matches_runner_order: True

## CSV Roundtrip

- dev screening-style CSV roundtrip identical: true

## Lifecycle Summary

- `run_harness` and `run_harness_with_traces` each instantiate one harness per run, call `prepare([])` once, sort by `(session_id, turn_index, id)`, maintain one mutable session dict per session id, and map answers directly by `task['id']`.
- The parity test produced identical dev answer dicts, so trace collection does not change Harness lifecycle or predictions.

## Dev vs Screening Structural Profile

- dev profile: {"record_keys": ["id", "type", "value"], "record_type_count": 26, "session_count": 83, "session_size_max": 4, "session_size_min": 1, "task_count": 120, "top_keys": ["available_actions", "device_state", "id", "personal_memory", "prompt", "schema", "session_id", "split", "turn_index", "visible_history"], "unique_task_id_count": 120}
- screening profile: {"record_keys": ["id", "type", "value"], "record_type_count": 28, "session_count": 176, "session_size_max": 4, "session_size_min": 1, "task_count": 700, "top_keys": ["available_actions", "device_state", "id", "personal_memory", "prompt", "schema", "session_id", "split", "turn_index", "visible_history"], "unique_task_id_count": 700}
- top-level keys only in dev: []
- top-level keys only in screening: []
- record keys only in dev: []
- record keys only in screening: []

## Cause Classification

- A. Submission pipeline error: not reproduced. Alignment, schema validation, lifecycle parity, and CSV roundtrip passed.
- B. Local evaluator overestimation: plausible. The local evaluator is notebook-compatible but self-contained and uses partial-credit F1/set matching; server scoring may be stricter and uses hidden screening references.
- C. Dev-screening structure difference: no blocking structural mismatch found; screening has the same core top-level and record-key shape needed by the harness.
- D. Actual generalization failure: still plausible because pipeline parity passed and public screening references are hidden.
