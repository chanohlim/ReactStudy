# Content Scope Decision Table

1. Blocked or held -> `none`.
2. Unresolved user confirmation controls content use -> `none` with confirmation required.
3. Local/internal or status update with `proceed` -> `status_only`.
4. Safe automatic redaction with concrete removable fields -> `redacted`.
5. Summary request or raw-detail reduction -> `summary`.
6. Resolved proceed with no active restriction -> `raw`.
7. Fallback executable scope -> safe `summary`.

The table depends on normalized scope evidence and should not be implemented as `control -> mode` mapping.
