# SCPC 2026 Problem Structure Notes

## Input → Harness → Output flow
Tasks are JSONL records with `schema`, `id`, `session_id`, `turn_index`, `prompt`, `visible_history`, `device_state`, `personal_memory`, and `available_actions`. The runner sorts by `(session_id, turn_index, id)`, maintains a per-session dictionary, passes a participant-safe task view into `FinalHarness.answer_task(task, session)`, and stores each returned answer under the task id.

## Main task data sources
- `prompt`: current user request.
- `visible_history`: summarized prior turns; use `turn` when present rather than assuming array priority.
- `device_state.objects`: candidate focal entities such as messages, files, calendar events, payments, settings, health items, and routines. Each object has `id`, `type`, and domain-specific `attrs`.
- `device_state.records`: auxiliary state signals such as resolved target, ambiguity, consent, security, policy, or memory updates.
- `personal_memory`: long-term user memory candidates.
- `available_actions`: verbs available for plan construction.

## Answer fields
The schema requires `focal_id`, `target`, `control`, `content_scope`, `policy`, and `plan_events`. `control` is one of `proceed`, `amend`, `hold`, or `ask`. `content_scope.mode` is one of `raw`, `summary`, `redacted`, `status_only`, or `none`. `policy` contains `risk_flags`, `violations`, and `requires_confirmation`. `plan_events` is an array of up to 18 `{verb, target, args}` objects.

## Session state
The baseline keeps one mutable session dict per `session_id` and records recent focal, target, control, and evidence after each turn. The harness also has an internal memory dictionary for records of type `persistent_memory_write`.

## FixedSLM evidence
`FixedSLMClient.summarize_task()` is a local deterministic facade. It scans prompt, records, and personal memory text and returns `risk_flags`, `requires_redaction`, `requires_confirmation`, and `audit_tags`. This is evidence only, not a direct answer.

## Baseline structure
The notebook baseline defines helpers for loading data, stripping scoring-only task keys, running the harness, validating payloads, approximating dev scoring, and writing `submission.csv`. `FinalHarness` is organized as `update_session_memory`, `choose_focal`, `infer_target`, `decide_control`, `build_content_scope`, `build_policy`, `build_plan_events`, and `user_response`.

## Local evaluation
The notebook includes a public dev scorer with weighted axes: focal, target, control, content_scope, policy, plan, semantic_response, and counterfactual. It is documented as an approximate local dev scorer, not necessarily identical to server scoring.

## Unclear or deliberately unspecified
The official materials do not provide private scoring internals, exhaustive object-type semantics, or a guarantee that array order within objects/records/memory implies priority. These should remain explicit uncertainty points during harness improvements.
