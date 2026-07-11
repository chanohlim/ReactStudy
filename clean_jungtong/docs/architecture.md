# 아키텍처
React/Vite PWA가 Supabase Auth 세션을 유지하고 Access Token을 FastAPI에 전달한다. FastAPI는 JWKS를 캐시해 JWT 서명, 만료, issuer, audience, subject를 검증한다. 데이터는 Supabase PostgreSQL에 저장하며 SQLAlchemy 2.x 동기식 세션을 사용한다. 생활관 범위 데이터는 `room_id`와 서버 측 membership 검사로 격리한다.

Cron은 앱 내부 스케줄러가 아니라 Supabase Cron/pg_net이 `CRON_SECRET` Bearer 토큰으로 Render의 내부 API를 호출한다.
