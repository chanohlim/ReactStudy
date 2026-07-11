# Content Scope Decision Boundaries

- `status_only` vs `none`: use `status_only` when a local/internal update still occurs; use `none` when no content can be used before confirmation or because execution is blocked.
- `redacted` vs `summary`: use `redacted` for concrete removable fields; use `summary` when the whole representation should be reduced.
- `raw` vs `summary`: use `raw` only after deciding there is no active scope restriction.
- `ask` vs `requires_user_confirmation`: `control=ask` describes the next action; `requires_user_confirmation` describes whether the selected content scope itself needs confirmation.
