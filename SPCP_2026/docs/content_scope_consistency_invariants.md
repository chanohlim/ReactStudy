# Content Scope Consistency Invariants

- `mode=none` should not contain broad `allowed_fields`.
- `mode=status_only` should expose `status` as the primary allowed field.
- `mode=redacted` should have concrete `excluded_fields`; otherwise fallback is safer.
- `mode=raw` should not have active exclusions.
- `control=hold` should not dispatch usable content.
- Local/internal updates should not expose raw external-dispatch content.
