# Control Semantics

## Working definition
`control` is the execution mode for the current task after focal and target are resolved: proceed as-is, proceed after safe amendment, hold execution, or ask the user. It is downstream of `focal_id` and `target`: focal identifies what is handled, target identifies where it applies, and control decides how or whether it can be applied.

## Four controls
- `proceed`: current state is executable without unresolved mandatory user choice and without required automatic narrowing. This includes local/internal updates and cases where older ambiguity is resolved by current records.
- `amend`: the original request is too broad or unsafe as stated, but the agent can apply a safe, meaningful scope reduction such as redaction or summary-only dispatch while preserving the goal.
- `ask`: the agent cannot choose one correct execution state without user input, e.g. unresolved recipient/scope/precondition, target change confirmation, memory conflict, or high-impact user choice.
- `hold`: execution is currently prohibited or unsafe; user confirmation alone is not enough unless the active state is explicitly a resolvable user-choice boundary.

## Relationships
- Control uses focal to inspect content sensitivity and removable fields.
- Control uses target to distinguish external dispatch, `user` clarification, and `memory_store` local update.
- `content_scope` should be a consequence of control, not an input oracle: `amend` implies an actual narrowing, `ask` implies confirmation, `hold` implies no executable content.
- Policy should explain risks and violations behind the control decision, but `policy.requires_confirmation` and `control=ask` are not assumed identical.
- Plan archetypes should follow control: proceed/update or dispatch, amend/redact then dispatch, ask/clarify, hold/guard.

## State precedence
Current local/internal update supersedes older external dispatch risk, target ambiguity, and external redaction requirements. Current target corrections and explicit user-choice boundaries supersede older resolved route. Security, consent, and non-removable health-detail violations block external execution unless a newer local-only update makes dispatch irrelevant.

## Confirmation semantics
FixedSLM confirmation evidence is only auxiliary. Confirmation-like words or ambiguity records alone do not force `ask`; the normalized state must show an unresolved user choice that remains active after target/local-update precedence.

## Unresolved questions
Some remaining misses require better separation between health detail that can be redacted and health detail that makes external execution non-resolvable. Future content_scope and policy work should tighten this without using answer fields as runtime evidence.
