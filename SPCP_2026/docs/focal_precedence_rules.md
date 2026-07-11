# Focal Precedence Rules

## F-01 Direct current object id
**Rule:** If a current record value directly names an object id present in `device_state.objects`, create a high-priority candidate.
**Reason:** An explicit object id is already resolved against the current task object set.
**Known limitation:** Nested lists are not deeply traversed yet; this avoids broad accidental matches.

## F-02 Structured latest phase chain
**Rule:** Resolve `focal_resolution_trace.latest_phase` or the phase indicated by `route_binding_order` through `phase_to_marker`, then resolve that marker through `focal_marker_refs.marker_to_ref`, and finally match the resulting ref_code to an object.
**Reason:** This follows explicit structured state inside the task rather than prompt text or object order.
**Evidence shape:** `latest_phase=boundary`, `boundary->marker_alpha`, `marker_alpha->WM-6361`, `WM-6361->obj...`.
**Known limitation:** If any chain link is missing or malformed, the resolver safely falls back.

## F-03 Current structure overrides history
**Rule:** A structured current pointer outranks visible history ref_code matches.
**Reason:** Current records describe the active turn's resolved state; history is prior context and can be stale.

## F-04 Visible history ref_code fallback
**Rule:** If no stronger current pointer resolves, an object whose `attrs.ref_code` appears in `visible_history` becomes a medium-priority candidate.
**Reason:** The official task structure documents history as summarized prior context; ref_code is an explicit object attribute.
**Known limitation:** History can mention stale objects, so it does not outrank current structured pointers.

## F-05 Prompt/object overlap fallback
**Rule:** If no explicit or structured evidence resolves focal, rank objects by token overlap between prompt and object text.
**Reason:** This preserves baseline behavior as a safe low-priority fallback for tasks without structured references.
**Known limitation:** It can confuse target/recipient text with content source text.
