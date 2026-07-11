# Policy / Plan Implementation Summary

This compact report contains aggregate metrics only; no task-level prediction or trace dumps are committed.

## Schema Summary

- `policy` requires `risk_flags`, `violations`, and `requires_confirmation`.
- `plan_events` is a list of objects with `verb`, `target`, and `args`.
- Dev references score plans against `expected_events`; observed archetypes are `read→verify→update`, `read→redact→dispatch`, `read→clarify`, `read→guard`, `read→dispatch`, and `read→summarize→dispatch`.

## Before / After

- Overall: 0.5671 -> 0.6458
- Focal: 0.8833 -> 0.8833
- Target: 0.8000 -> 0.8000
- Control: 0.7000 -> 0.7000
- Content Scope: 0.5008 -> 0.5008
- Policy: 0.3555 -> 0.5532
- Plan: 0.3044 -> 0.5986
- Policy@Correct Focal+Target+Control+ContentScope: 0.2980 -> 0.9125
- Plan@Correct Focal+Target+Control+ContentScope: 0.7000 -> 1.0000

- Exact policy count: 0 -> 7 (newly correct 7, newly wrong 0)
- Exact plan count: 2 -> 73 (newly correct 71, newly wrong 0)

## Policy Component Accuracy After

- risk_flags: 0.7031
- violations: 0.9417
- requires_confirmation: 0.8167

## Plan Component Accuracy After

- sequence: 0.7083
- count: 0.9000
- first: 1.0000
- final: 0.8417
- verb_f1: 0.8736

## Ablation

| Variant | Overall | Policy | Plan | Control | Content Scope | Policy@CFTCS | Plan@CFTCS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full | 0.6458 | 0.5532 | 0.5986 | 0.7000 | 0.5008 | 0.9125 | 1.0000 |
| no_plan_archetype_table | 0.5929 | 0.5532 | 0.3044 | 0.7000 | 0.5008 | 0.9125 | 0.7000 |
| no_policy_from_control | 0.6373 | 0.5053 | 0.5861 | 0.7000 | 0.5008 | 0.5021 | 0.8750 |
| no_policy_from_scope | 0.6401 | 0.5090 | 0.5986 | 0.7000 | 0.5008 | 0.9091 | 1.0000 |
| no_cross_field_validator | 0.6458 | 0.5532 | 0.5986 | 0.7000 | 0.5008 | 0.9125 | 1.0000 |
| no_summary_plan | 0.6463 | 0.5532 | 0.6016 | 0.7000 | 0.5008 | 0.9125 | 1.0000 |
| no_redaction_plan | 0.6449 | 0.5532 | 0.5936 | 0.7000 | 0.5008 | 0.9125 | 1.0000 |
| no_hold_guard_plan | 0.6361 | 0.5532 | 0.5444 | 0.7000 | 0.5008 | 0.9125 | 0.4583 |

## Remaining Failure Types

- Policy risk flags still underfit some target/precondition combinations because the builder uses runtime records rather than task-specific labels.
- Plan exactness is still limited by upstream content_scope/control errors and by nuanced `remove=raw_quote` versus `remove=sensitive_fields` boundaries.
