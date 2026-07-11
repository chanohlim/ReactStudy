# Control Error Taxonomy Before Upgrade

Before the control upgrade, control exact matches were 37/120 overall. On the core subset where focal and target were both correct, control accuracy was 24/96 = 0.25.

## Group A: focal correct + target correct + control wrong
Major failure families:

1. **Stale ambiguity over-ask**
   - Confusion: expected `proceed`/`amend`/`hold`, predicted `ask`.
   - Structure: ambiguity records existed, but current target/local state or safe amendment resolved the active decision.
   - Fix: distinguish active user choice from stale/superseded ambiguity.

2. **Local update control failure**
   - Confusion: expected `proceed`, predicted `ask`/`amend`/`hold`.
   - Structure: latest local/internal update made external dispatch risk irrelevant.
   - Fix: local update precedence before blocking/amend/ask.

3. **Safe narrowing failure**
   - Confusion: expected `amend`, predicted `ask` or `proceed`.
   - Structure: sensitive fields or policy could be automatically narrowed while preserving the request.
   - Fix: safe_redaction_possible + goal_preserved branch.

4. **Ask vs hold boundary failure**
   - Confusion: expected `hold`, predicted `ask`, or expected `ask`, predicted `hold`.
   - Structure: some blocked states were resolvable by user choice; others were active violations.
   - Fix: separate user-resolvable boundary from non-resolvable violation.

## Group B/C: upstream cascade
Errors with wrong focal and/or target are tracked separately and were not used to modify focal or target resolver logic in this phase.

## Regression risk
Remaining regressions mainly involve ambiguous_focal external candidate cases and health-detail boundaries where the distinction between ask/amend/hold still needs better semantic evidence.
