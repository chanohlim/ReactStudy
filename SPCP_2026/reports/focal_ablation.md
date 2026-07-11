# Focal Resolver Ablation

| Variant | Overall | Focal | Correct | Wrong |
| --- | ---: | ---: | ---: | ---: |
| full | 0.2886 | 0.8833 | 106 | 14 |
| no_structured_chain | 0.0982 | 0.3167 | 38 | 82 |
| no_direct_record | 0.2886 | 0.8833 | 106 | 14 |
| no_history_ref | 0.2491 | 0.7500 | 90 | 30 |
| no_prompt_overlap | 0.2886 | 0.8833 | 106 | 14 |

## Interpretation
- `no_structured_chain` isolates the contribution of the phase → marker → ref_code → object resolver.
- `no_direct_record`, `no_history_ref`, and `no_prompt_overlap` check whether fallback families are carrying meaningful examples or mainly preserving safety.
- The full resolver keeps explicit fallback behavior so malformed chains do not abort a run.
