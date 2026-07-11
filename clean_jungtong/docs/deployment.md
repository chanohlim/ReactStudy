# 배포

## Vercel
`frontend`를 Root Directory로 지정하고 환경변수 `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_VAPID_PUBLIC_KEY`를 설정한다. `frontend/vercel.json`이 SPA rewrite를 처리한다.

## Render
`backend`를 Docker Web Service로 배포한다. 환경변수는 `backend/.env.example`을 기준으로 설정한다. 시작 시 자동 Alembic 실행은 하지 않는다. 배포 전 별도 작업으로 `alembic upgrade head`를 실행한다.

## Supabase Cron 예시
20:50 KST = 11:50 UTC, 21:00 KST = 12:00 UTC.

```sql
select cron.schedule('schedule-reminder','50 11 * * *',$$select net.http_post(url:='https://YOUR-API.onrender.com/api/internal/jobs/schedule-reminder', headers:='{"Authorization":"Bearer YOUR_CRON_SECRET"}'::jsonb);$$);
select cron.schedule('daily-draw','0 12 * * *',$$select net.http_post(url:='https://YOUR-API.onrender.com/api/internal/jobs/daily-draw', headers:='{"Authorization":"Bearer YOUR_CRON_SECRET"}'::jsonb);$$);
```

무료 플랜 정책과 제한은 배포 직전 공식 문서에서 다시 확인한다.
