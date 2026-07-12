# Control Consistency Invariants

- `control=proceed` should not have active unresolved mandatory user choice.
- `control=amend` should correspond to a real scope/action narrowing, not just generic risk.
- `control=ask` should lead to clarification rather than immediate external dispatch.
- `control=hold` should not produce an unsafe execution event.
- Local/internal update decisions should not be blocked by stale external dispatch risk.
- FixedSLM redaction/confirmation signals are evidence only; they should not directly force `amend` or `ask` without supporting current state.
