# Control Decision Boundaries

## Proceed vs ask
Proceed is valid when ambiguity is already resolved by current route/target state or superseded by local update. Ask is reserved for unresolved recipient, scope, precondition, or target-change decisions that cannot be chosen from current state alone.

## Proceed vs amend
Proceed keeps the effective action semantics unchanged. Amend is used when an external request remains feasible only after automatic safe narrowing, such as removing raw/sensitive fields or applying a summary-only policy.

## Amend vs ask
Amend is chosen when the agent can safely reduce scope without requiring the user to choose among alternatives. Ask is chosen when the agent needs user selection or confirmation before it can know the correct destination, scope, or precondition.

## Ask vs hold
Ask means user input can resolve the active uncertainty. Hold means the current state is unsafe or prohibited and a simple confirmation is insufficient, such as revoked consent, active security/safety signal, or non-removable external health-detail exposure.

## Local update boundary
When a newer local/internal state update cancels external dispatch, control is `proceed` even if older external-share, ambiguity, consent, or security signals exist, because the risky dispatch is no longer the active action.
