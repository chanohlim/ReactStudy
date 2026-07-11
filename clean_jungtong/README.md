# 생활관 청소 추첨 PWA

모바일 중심 PWA로 생활관 구성원이 야간근무·부재 일정을 등록하면 매일 21:00 KST에 다음 날 청소자를 미세 가중 랜덤으로 추첨하는 서비스입니다.

## 구현 범위
- React/Vite/TypeScript/Tailwind PWA 스캐폴딩과 한국어 모바일 UI.
- Supabase Auth 세션 기반 로그인/회원가입 UI와 FastAPI Bearer JWT 검증 구조.
- 생활관 생성, 초대 토큰 해시 저장, 초대 가입, 구성원/일정/청소 설정 API 골격.
- 공용구역 주간 순환, 호실 청소 빈도 검증, 미세 가중 랜덤 순수 함수와 테스트.
- PostgreSQL용 SQLAlchemy 모델과 Alembic 초기 마이그레이션.
- Web Push service worker, VAPID 공개키 API, Cron 내부 API 골격.

## 주요 가정
- MVP에서 사용자는 하나의 활성 생활관만 가진다.
- 군번, 상세 부대명, 근무표 이미지 등 민감 군 정보는 저장하지 않는다.
- PostgreSQL enum 대신 문자열 enum을 사용한다.
- Render 시작 시 Alembic 자동 실행은 하지 않고 배포 단계에서 수동 실행한다.
- Codex 환경에서는 npm/pip 설치를 실행하지 않았으므로 lock 파일은 사용자가 설치 시 생성/갱신한다.

## 로컬 실행
자세한 설치·검증은 `docs/manual-installation.md`를 참고하세요.

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd ../backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## 환경변수
프론트엔드: `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `VITE_VAPID_PUBLIC_KEY`.
백엔드: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_JWT_ISSUER`, `SUPABASE_JWT_AUDIENCE`, `SUPABASE_JWKS_URL`, `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT`, `CRON_SECRET`, `FRONTEND_ORIGIN`, `ENVIRONMENT`, `TIMEZONE`.

## 배포
Vercel은 `frontend` root, Render는 `backend/Dockerfile`을 사용합니다. Supabase 마이그레이션과 Cron 예시는 `docs/deployment.md`에 있습니다.
