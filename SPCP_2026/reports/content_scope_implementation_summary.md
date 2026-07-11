# Content Scope Implementation Summary

This compact summary contains aggregate metrics only; no task-level prediction or trace dumps are committed.

## Second-Pass Failure Analysis

- Raw failures were mainly safe `proceed` dispatch cases being absorbed by `status_only` or summary fallback because every `share_boundary_update` was treated like a local/status boundary. The revised logic treats only explicit local update boundaries as `status_only`; weak external boundary signals no longer override safe raw dispatch.
- Summary failures were mainly unresolved `ask` or explicit summary-share cases being forced to `none`. The revised decision table allows summary scope with `requires_user_confirmation=True` when the content can be summarized but action confirmation is still pending.
- Redacted failures remain mostly field-boundary issues: the second pass improves original field names (`name`, `rrn`, `numeric_value`, `location`, `raw_quote`) and avoids using broad identifier/payment aliases that do not match the official answer fields.
- Confirmation ablation suggested over-application. The revised logic keeps guard/hold and local/status updates confirmation-free, while preserving confirmation for unresolved ask scopes and ask-time summary/redaction scopes.

## Previous Stable -> Current

- Overall: 0.5601 -> 0.5671
- Focal: 0.8833 -> 0.8833
- Target: 0.8000 -> 0.8000
- Control: 0.7000 -> 0.7000
- Content Scope: 0.4499 -> 0.5008
- Content Scope@Correct Focal+Target+Control: 0.7012 -> 0.7805
- Exact content scope count: 20 -> 22
- Newly correct exact scopes: 3
- Newly wrong exact scopes: 1

## Mode Accuracy Previous -> Current

- none: 0.8182 -> 0.6818
- raw: 0.0000 -> 0.5000
- redacted: 0.4167 -> 0.3611
- status_only: 0.9000 -> 0.9000
- summary: 0.0000 -> 0.4444

## Part Accuracy Current

- allowed_fields: 0.7194
- excluded_fields: 0.6214
- mode: 0.6167
- requires_user_confirmation: 0.8750

## Baseline Legacy -> Current

- Overall: 0.5449 -> 0.5671
- Content Scope: 0.3466 -> 0.5008
- Content Scope@Correct Focal+Target+Control: 0.5402 -> 0.7805

## Ablation

| Variant | Overall | Focal | Target | Control | Content Scope | Exact Scope | Scope@CFT |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full | 0.5671 | 0.8833 | 0.8000 | 0.7000 | 0.5008 | 22 | 0.7805 |
| no_local_status_only | 0.5386 | 0.8833 | 0.8000 | 0.7000 | 0.3329 | 17 | 0.5188 |
| no_redacted_scope | 0.5519 | 0.8833 | 0.8000 | 0.7000 | 0.4581 | 23 | 0.7140 |
| no_summary_scope | 0.5606 | 0.8833 | 0.8000 | 0.7000 | 0.4625 | 20 | 0.7208 |
| no_none_scope | 0.5682 | 0.8833 | 0.8000 | 0.7000 | 0.5075 | 21 | 0.7908 |
| no_requires_confirmation_logic | 0.5670 | 0.8833 | 0.8000 | 0.7000 | 0.5000 | 19 | 0.7792 |
| no_fixed_slm_scope_evidence | 0.5671 | 0.8833 | 0.8000 | 0.7000 | 0.5008 | 22 | 0.7805 |

## Remaining Failure Types

- Redacted exact accuracy regressed slightly because ask-time redaction/summary boundaries now compete more explicitly; remaining work should refine when a confirmation-pending share still expects redacted rather than summary.
- None mode regressed because some confirmation-pending cases now keep a usable summary scope. The distinction between pure clarification and summary-with-confirmation remains the largest boundary risk.
- FixedSLM scope evidence still has no aggregate effect, which is acceptable because it is auxiliary evidence rather than an oracle.
