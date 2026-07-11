# SCPC 2026 AI Challenge Rulebook

This project builds a Python-only Agent Harness for SCPC 2026. The goal is a generalizable harness for unseen task streams, not a lookup table for public examples.

## Official interface
```python
class FinalHarness:
    def __init__(self):
        self.slm = FixedSLMClient()
        self.user_memory = {}
    def answer_task(self, task, session):
        ...
        return answer
```

Final answers must include `focal_id`, `target`, `control`, `content_scope`, `policy`, and `plan_events` under the official submission schema.

## Core constraints
1. Use Python only.
2. Do not use external LLM APIs or external models for final inference.
3. Final inference may use only the official local `FixedSLMClient` facade as evidence.
4. Never hardcode specific `task_id`, `session_id`, public example sentence, or evaluation answer.
5. Do not analyze the 700 screening tasks to derive task-specific rules, answer distributions, or manual fixes.
6. Use `dev_tasks` and `dev_answers` only for allowed development, schema validation, and local evaluation.
7. Improvements must be semantic or structural general rules expected to transfer to new tasks.
8. Preserve `FinalHarness.answer_task(task, session)`.
9. Preserve official schema and single-cell CSV submission format.

## Evaluation and submission
Generate answers for all screening tasks, serialize the full answer JSON into the single `submission` column and one data row of `submission.csv`, UTF-8 encoded. Local dev metrics are for engineering feedback only unless explicitly official.

## Engineering principle
Build parser, session memory, safety/control logic, content scope, and plan construction that explain decisions and generalize. Do not optimize this phase for leaderboard score.
