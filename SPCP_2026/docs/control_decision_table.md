# Control Decision Table

1. **Is the latest active action a local/internal update?**
   - Yes → `proceed` (`C-01`), because external dispatch and older share-risk signals are superseded.
2. **Is the active action blocked?**
   - Yes, and user choice can resolve it without active security/safety/consent violation → `ask` (`C-02`).
   - Yes, and user confirmation alone is insufficient → `hold` (`C-03`).
3. **Is a mandatory user choice still unresolved?**
   - Yes → `ask` (`C-04`).
4. **Does original execution require narrowing, and can the agent safely perform it while preserving the goal?**
   - Yes → `amend` (`C-05`).
5. **Otherwise**
   - `proceed` (`C-06`).

The implementation uses this as a deterministic decision table over a normalized `ControlContext` rather than a class-frequency guess or a single keyword rule.
