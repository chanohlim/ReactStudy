# Control Answer Structure Analysis

Control correlates with output fields, but those fields are consequences, not runtime inputs.

- `proceed` often pairs with executable update/dispatch plans and may still have risk-related context when the active action is local-only or already resolved.
- `amend` pairs with redacted or narrowed scope and redaction plan events; it represents automatic safe narrowing.
- `ask` pairs with confirmation/clarification behavior and usually indicates unresolved user choice, target/scope ambiguity, or changed precondition.
- `hold` pairs with guard/no-dispatch behavior and reflects non-resolvable active violations or unsafe state.

Runtime evidence used by the control engine is limited to task records, focal attrs, resolved target, session memory state, and FixedSLM auxiliary evidence. Reference fields such as expected plan events and expected policy are not used as decision inputs.
