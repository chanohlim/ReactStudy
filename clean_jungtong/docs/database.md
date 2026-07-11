# 데이터베이스
초기 마이그레이션은 `backend/alembic/versions/0001_initial_schema.py`에 있다. 주요 테이블은 profiles, rooms, room_members, room_invites, availability_events, room_cleaning_settings, weekly_zone_overrides, draw_runs, draw_tasks, draw_candidates, draw_exclusions, cleaning_assignments, push_subscriptions, audit_logs, job_runs이다.

문자열 enum을 사용해 운영 중 enum 값 추가 시 마이그레이션 위험을 줄였다. 초대 토큰은 SHA-256 해시만 저장한다. `draw_runs`는 `(room_id, target_date, is_active)` 고유 제약으로 활성 추첨 중복을 방지한다.

## 데모 seed
실제 Supabase Auth 사용자는 자동 생성하지 않는다. Supabase에서 관리자 1명과 구성원 5명을 만든 뒤 해당 UUID를 profiles/room_members에 넣고, 야간근무·휴가·이전 청소 기록을 삽입해 시연한다.
