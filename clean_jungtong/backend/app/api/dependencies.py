from fastapi import Depends,Header,HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_supabase_token,verify_cron_secret
from app.models import Profile,RoomMember
def current_profile(authorization:str=Header(...),db:Session=Depends(get_db)):
    token=authorization.removeprefix('Bearer ').strip(); claims=verify_supabase_token(token); sub=claims['sub']; email=claims.get('email','')
    profile=db.query(Profile).filter(Profile.supabase_user_id==sub).first()
    if not profile:
        profile=Profile(supabase_user_id=sub,email=email,display_name=email.split('@')[0] or '사용자'); db.add(profile); db.commit(); db.refresh(profile)
    return profile
def require_cron(authorization:str|None=Header(default=None)): verify_cron_secret(authorization)
def active_member(room_id,profile,db:Session,admin:bool=False):
    q=db.query(RoomMember).filter_by(room_id=room_id,profile_id=profile.id,is_active=True); m=q.first()
    if not m or (admin and m.role!='ADMIN'): raise HTTPException(status_code=403,detail='생활관 권한이 없습니다.')
    return m
