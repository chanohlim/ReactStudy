# 구현 계획

## 가정
- 작업 루트는 `clean_jungtong`이며 새 모노레포로 구성한다.
- MVP는 한 사용자의 활성 생활관을 하나로 제한한다.
- Enum은 Alembic 유지보수를 위해 PostgreSQL enum 대신 문자열 컬럼을 사용한다.
- Codex는 npm/pip 설치를 실행하지 않으며 manifest와 소스만 작성한다.

## Phase 상태
1. 분석과 기반 구축: 완료 — 문서, 프론트/백엔드 스캐폴딩, DB 모델, 초기 마이그레이션 작성.
2. 인증과 생활관: 부분 완료 — Supabase JWT 검증, 프로필 동기화, 생활관/초대/가입 API와 기본 UI 작성.
3. 일정과 청소 설정: 부분 완료 — 일정 API, 야간근무 원터치 UI, 호실 청소 UI/검증 작성.
4. 추첨 엔진: 부분 완료 — 순수 가중 랜덤/순환 로직, idempotent draw run 골격 작성. 후보 스냅샷 저장은 추가 구현 필요.
5. 완료·리더보드·로그: 부분 완료 — API 골격 작성. 집계 상세 구현 필요.
6. PWA·웹푸시·Cron: 부분 완료 — manifest, service worker, push subscription API 골격, cron endpoint 작성.
7. 테스트와 배포: 부분 완료 — 핵심 순수 함수 테스트, Docker/Vercel/문서 작성. 설치 후 전체 검증 필요.
