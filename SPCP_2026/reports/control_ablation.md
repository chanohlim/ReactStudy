# Control Ablation

| Variant | Overall | Focal | Target | Control | Control Correct | Control@Focal+Target |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| full | 0.5449 | 0.8833 | 0.8000 | 0.7000 | 95 | 0.8021 |
| no_local_precedence | 0.5398 | 0.8833 | 0.8000 | 0.6833 | 92 | 0.7812 |
| no_safe_amend | 0.4693 | 0.8833 | 0.8000 | 0.5750 | 80 | 0.6458 |
| no_user_choice | 0.4900 | 0.8833 | 0.8000 | 0.5500 | 75 | 0.6667 |
| no_blocking | 0.5282 | 0.8833 | 0.8000 | 0.6667 | 91 | 0.7604 |
| no_fixed_slm_evidence | 0.5449 | 0.8833 | 0.8000 | 0.7000 | 95 | 0.8021 |

## Interpretation
- `no_local_precedence` isolates local/internal update superseding older ambiguity, security, consent, and external-redaction signals.
- `no_safe_amend` measures automatic scope-narrowing/redaction feasibility.
- `no_user_choice` measures unresolved user decision and target/precondition ambiguity handling.
- `no_blocking` measures non-resolvable safety/policy blocking.
- `no_fixed_slm_evidence` confirms FixedSLM is auxiliary and not an oracle.
