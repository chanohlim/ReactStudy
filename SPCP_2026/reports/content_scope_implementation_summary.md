# Content Scope Implementation Summary

This compact summary contains aggregate metrics only; no task-level prediction or trace dumps are committed.

## Before / After
- Overall: 0.5449 -> 0.5601
- Focal: 0.8833 -> 0.8833
- Target: 0.8000 -> 0.8000
- Control: 0.7000 -> 0.7000
- Content Scope: 0.3466 -> 0.4499
- Content Scope@Correct Focal+Target+Control: 0.5402 -> 0.7012

## Part Accuracy After
- allowed_fields: 0.6000
- excluded_fields: 0.5516
- mode: 0.5750
- requires_user_confirmation: 0.8750

## Mode Accuracy After
- none: 0.8182
- raw: 0.0000
- redacted: 0.4167
- status_only: 0.9000
- summary: 0.0000

## Ablation

| Variant | Overall | Focal | Target | Control | Content Scope | Exact Scope | Scope@CFT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full | 0.5601 | 0.8833 | 0.8000 | 0.7000 | 0.4499 | 20 | 0.7012 |
| no_local_status_only | 0.5320 | 0.8833 | 0.8000 | 0.7000 | 0.2846 | 15 | 0.4436 |
| no_redacted_scope | 0.5421 | 0.8833 | 0.8000 | 0.7000 | 0.4040 | 20 | 0.6297 |
| no_summary_scope | 0.5601 | 0.8833 | 0.8000 | 0.7000 | 0.4499 | 20 | 0.7012 |
| no_none_scope | 0.5611 | 0.8833 | 0.8000 | 0.7000 | 0.4567 | 19 | 0.7118 |
| no_requires_confirmation_logic | 0.5670 | 0.8833 | 0.8000 | 0.7000 | 0.4908 | 19 | 0.7648 |
| no_fixed_slm_scope_evidence | 0.5601 | 0.8833 | 0.8000 | 0.7000 | 0.4499 | 20 | 0.7012 |
