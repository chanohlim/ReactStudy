# Focal Error Taxonomy Before Resolver Change

Baseline: `reports/runs/focal_before.json`.

## marker/reference chain failure
- Count: 72
- Common structure: records include `focal_resolution_trace` and `focal_marker_refs`, but the baseline does not follow phase → marker → ref_code → object.
- Why baseline failed: it only checked direct object ids in record values, history ref_codes, then prompt overlap.
- General fix: implement a structured reference chain resolver that follows current task records without task-id or prompt exact matching.
- Representative examples: `final_dev_5700ad3a5bb3`, `final_dev_8972f1090f6b`, `final_dev_b0696e0a0b55`.

## visible history reference failure
- Count: 13
- Common structure: expected focal has a ref_code present in visible history, but weaker prompt overlap or stale surface text wins.
- Why baseline failed: history was used, but only after direct record id scan and before simplistic overlap; structured current evidence was absent or malformed in these examples.
- General fix: keep history ref_code as a named candidate source and make its precedence explicit above prompt overlap.
- Representative examples: `final_dev_25d2f58cdc0b`, `final_dev_5ebf0fd867b8`, `final_dev_ccb58d8b17ed`.

## remaining risk categories to monitor
- Focal/target confusion when recipient/channel strings appear in object attrs.
- Stale object selection when history contains previous but no current pointer exists.
- Fallback ranking failure when multiple objects share the same prompt body or similar attrs.
