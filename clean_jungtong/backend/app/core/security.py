import time,httpx
from jose import jwt
from jose.exceptions import JWTError
from fastapi import HTTPException,status
from .config import settings
_cache={'keys':None,'expires':0.0}
def get_jwks():
    if _cache['keys'] and _cache['expires']>time.time(): return _cache['keys']
    r=httpx.get(settings.supabase_jwks_url,timeout=5); r.raise_for_status(); _cache.update(keys=r.json(),expires=time.time()+3600); return _cache['keys']
def verify_supabase_token(token:str)->dict:
    try:
        return jwt.decode(token,get_jwks(),algorithms=['RS256','ES256'],audience=settings.supabase_jwt_audience,issuer=settings.supabase_jwt_issuer,options={'verify_sub':True})
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='유효하지 않은 인증 토큰입니다.') from exc
def verify_cron_secret(header:str|None):
    if header != f'Bearer {settings.cron_secret}': raise HTTPException(status_code=401,detail='Invalid cron secret')
