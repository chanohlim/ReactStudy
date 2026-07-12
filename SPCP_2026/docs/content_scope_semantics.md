# Content Scope Semantics

`content_scope` describes which portion of the focal object's content/state may be used for the selected action. It is downstream of focal, target, and control, but it is not a simple `control -> mode` lookup.

- `mode`: `raw`, `summary`, `redacted`, `status_only`, or `none`.
- `allowed_fields`: fields the harness may use in the selected mode.
- `excluded_fields`: fields intentionally removed from the usable scope.
- `requires_user_confirmation`: whether this content scope itself needs user confirmation before use.

Mode meanings:

- `raw`: direct use is allowed because no active redaction, summary, local-only, confirmation, or blocking boundary exists.
- `summary`: raw details should be reduced, but a summarized representation is enough.
- `redacted`: removable sensitive or disallowed fields must be excluded before use.
- `status_only`: the action is a local/internal state update, memory write, or status update rather than content dispatch.
- `none`: no content should be used because execution is held, blocked, or unresolved.

Runtime evidence should come from focal attrs, current records, target/control traces, ControlContext signals, session state when still valid, and FixedSLM auxiliary evidence. FixedSLM is not an oracle.
