# 수동 설치 및 검증

## 프론트엔드 설치
```bash
cd frontend
npm install
npm run dev
```

## 프론트엔드 검증
```bash
npm run typecheck
npm run lint
npm run test:run
npm run build
```

## 백엔드 설치
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

## 백엔드 실행
```bash
uvicorn app.main:app --reload
```

## 백엔드 검증
```bash
pytest
alembic upgrade head
```

## 문제 해결
- 권장 버전: Node.js 20.x, npm 10.x, Python 3.12.
- `node_modules` 재설치: `rm -rf node_modules package-lock.json && npm install`.
- package-lock 재생성: `frontend/package-lock.json`을 삭제한 뒤 사용자가 `npm install`을 실행한다.
- Codespaces 포트: Ports 탭에서 5173(Vite), 8000(FastAPI)을 Public/Private로 설정한다.
- 환경변수: `frontend/.env.example`, `backend/.env.example`을 `.env`로 복사하고 실제 값을 입력한다.
- CORS 오류: `FRONTEND_ORIGIN`이 Vite/Vercel origin과 정확히 일치하는지 확인한다.
- DB 연결 오류: `DATABASE_URL`의 host, password, SSL 요구 여부, Supabase connection string 형식을 확인한다.
