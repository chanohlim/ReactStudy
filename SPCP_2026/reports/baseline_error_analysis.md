# Baseline Error Analysis

Run: `reports/runs/run_001.json`

## Failure type counts

- plan construction failure: 120 (examples: final_dev_7286d93e3d0f, final_dev_a553e284342b, final_dev_25d2f58cdc0b)
- focal resolution failure: 85 (examples: final_dev_25d2f58cdc0b, final_dev_5700ad3a5bb3, final_dev_5ebf0fd867b8)
- control classification failure: 25 (examples: final_dev_7286d93e3d0f, final_dev_935d6c50ab4f, final_dev_1ada8b6f857e)
- target resolution failure: 21 (examples: final_dev_7286d93e3d0f, final_dev_a553e284342b, final_dev_1ada8b6f857e)
- policy inconsistency: 18 (examples: final_dev_8af3369d4151, final_dev_681d2e291ea5, final_dev_0a50781a4b36)
- content scope failure: 13 (examples: final_dev_8af3369d4151, final_dev_681d2e291ea5, final_dev_0a50781a4b36)

## General improvement candidates
- 최신 record와 session update의 우선순위를 명시하는 precedence rule 연구.
- focal/target/control의 의존 관계를 trace로 검증하는 consistency checker 추가.
- plan_events를 공식 action ontology에 더 안정적으로 매핑하는 일반 builder 개선.
