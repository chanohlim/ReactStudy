# Focal ID Semantics

## Working definition
`focal_id` is the current task object that the harness should treat as the main content-bearing or state-bearing object for the requested operation. It is an object id from `device_state.objects`, not a recipient string, app name, channel name, or policy record.

## Focal vs target
The focal object is the source or subject being read, guarded, summarized, updated, paid, toggled, or otherwise inspected. `target` is the destination, recipient, channel, device, app, merchant, user confirmation endpoint, or memory store that the action addresses. A message may mention a recipient while the focal object is a file, health record, payment request, calendar item, setting, or message body.

## Answers to the focal questions
1. Focal is not every object mentioned by the user; it is the single central object selected by current task evidence.
2. It is often the direct object of the first `read`, `verify`, `guard`, `redact`, or `update` step, while later `dispatch` may target a channel or recipient.
3. It is usually the request's principal content source or state source.
4. Target can be external to `objects`; focal should remain an object id.
5. With several actions, focal follows the object whose content/state must be inspected before deciding or acting, not necessarily the final dispatch target.
6. Current structured state should override older visible history when both exist; history is a fallback when no stronger current pointer is present.
7. Latest state updates can change focal when records expose a current phase or pointer chain.
8. Records can specify focal through a chain such as route phase → marker → ref_code → object.
9. Session memory can influence focal in principle, but this iteration only preserves existing session behavior and does not add broad memory-based focal rules.
10. Ambiguity is handled by collecting candidates and using explicit precedence; the trace exposes competing candidates.

## Data sources
- Direct object ids embedded in current records.
- Structured `focal_resolution_trace` plus `focal_marker_refs` chains.
- `visible_history` ref_code carry-over.
- Prompt/object attribute token overlap as a low-priority fallback.

## Precedence hypothesis
Current explicit/structured task records outrank history, and history outranks text overlap. This is semantic rather than distributional: current records represent device state for this turn; history is prior context; overlap is a weak lexical fallback.

## Ambiguous and unresolved cases
Ambiguous tasks may contain several plausible objects with similar surface text. If no direct id or structured chain exists, history and lexical fallback can still select stale or surface-level objects. Session-memory-based focal selection remains intentionally conservative and unresolved.
