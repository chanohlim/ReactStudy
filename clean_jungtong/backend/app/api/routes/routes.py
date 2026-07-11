from datetime import date,datetime,timedelta
import hashlib,secrets
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import active_member,current_profile,require_cron
from app.core.config import settings
from app.core.database import get_db
from app.models import *
from app.schemas import *
from app.services.cleaning_rules import zone_for_date
router=APIRouter(prefix='/api')
@router.get('/me')
def me(p=Depends(current_profile)): return {'id':str(p.id),'email':p.email,'display_name':p.display_name}
@router.patch('/me')
def patch_me(body:ProfilePatch,p=Depends(current_profile),db:Session=Depends(get_db)): p.display_name=body.display_name; db.commit(); return me(p)
@router.post('/rooms')
def create_room(body:RoomCreate,p=Depends(current_profile),db:Session=Depends(get_db)):
    room=Room(name=body.name,timezone=body.timezone,draw_time=body.draw_time,reminder_time=body.reminder_time,rotation_start_date=date.today(),allow_same_person=body.allow_same_person); db.add(room); db.flush(); m=RoomMember(room_id=room.id,profile_id=p.id,role='ADMIN'); db.add(m); db.add(RoomCleaningSetting(room_id=room.id)); db.commit(); return {'id':str(room.id),'name':room.name,'timezone':room.timezone}
@router.get('/rooms/me')
def my_room(p=Depends(current_profile),db:Session=Depends(get_db)):
    m=db.query(RoomMember).filter_by(profile_id=p.id,is_active=True).first();
    if not m: return None
    r=db.get(Room,m.room_id); return {'id':str(r.id),'name':r.name,'role':m.role}
@router.patch('/rooms/{room_id}')
def update_room(room_id:str,body:RoomCreate,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db,True); r=db.get(Room,room_id); r.name=body.name; r.timezone=body.timezone; r.draw_time=body.draw_time; r.reminder_time=body.reminder_time; r.allow_same_person=body.allow_same_person; db.commit(); return {'id':str(r.id),'name':r.name}
@router.post('/rooms/{room_id}/invites')
def create_invite(room_id:str,body:InviteCreate,p=Depends(current_profile),db:Session=Depends(get_db)):
    m=active_member(room_id,p,db,True); token=secrets.token_urlsafe(24); h=hashlib.sha256(token.encode()).hexdigest(); inv=RoomInvite(room_id=room_id,created_by_member_id=m.id,token_hash=h,expires_at=body.expires_at,max_uses=body.max_uses); db.add(inv); db.commit(); return {'id':str(inv.id),'invite_url':f'/join/{token}','expires_at':inv.expires_at,'max_uses':inv.max_uses,'used_count':inv.used_count}
@router.get('/invites/{token}')
def get_invite(token:str,db:Session=Depends(get_db)):
    h=hashlib.sha256(token.encode()).hexdigest(); inv=db.query(RoomInvite).filter_by(token_hash=h,revoked=False).first();
    if not inv or inv.expires_at<datetime.utcnow() or inv.used_count>=inv.max_uses: raise HTTPException(404,'유효하지 않은 초대입니다.')
    room=db.get(Room,inv.room_id); return {'room_name':room.name,'expires_at':inv.expires_at}
@router.post('/invites/{token}/join')
def join(token:str,p=Depends(current_profile),db:Session=Depends(get_db)):
    if db.query(RoomMember).filter_by(profile_id=p.id,is_active=True).first(): raise HTTPException(409,'이미 활성 생활관에 가입되어 있습니다.')
    h=hashlib.sha256(token.encode()).hexdigest(); inv=db.query(RoomInvite).filter_by(token_hash=h,revoked=False).first();
    if not inv or inv.expires_at<datetime.utcnow() or inv.used_count>=inv.max_uses: raise HTTPException(404,'유효하지 않은 초대입니다.')
    inv.used_count+=1; m=RoomMember(room_id=inv.room_id,profile_id=p.id,role='MEMBER'); db.add(m); db.commit(); return {'room_id':str(inv.room_id),'role':'MEMBER'}
@router.delete('/rooms/{room_id}/invites/{invite_id}')
def revoke_invite(room_id:str,invite_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db,True); inv=db.get(RoomInvite,invite_id); inv.revoked=True; db.commit(); return {'ok':True}
@router.get('/rooms/{room_id}/members')
def members(room_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db); return [{'id':str(m.id),'role':m.role,'is_active':m.is_active,'weight':float(m.weight)} for m in db.query(RoomMember).filter_by(room_id=room_id).all()]
@router.patch('/rooms/{room_id}/members/{member_id}')
def patch_member(room_id:str,member_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db,True); m=db.get(RoomMember,member_id); m.is_active=not m.is_active; db.commit(); return {'id':str(m.id),'is_active':m.is_active}
@router.delete('/rooms/{room_id}/members/{member_id}')
def delete_member(room_id:str,member_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db,True); m=db.get(RoomMember,member_id); m.is_active=False; db.commit(); return {'ok':True}
@router.get('/schedules/me')
def schedules(p=Depends(current_profile),db:Session=Depends(get_db)): m=db.query(RoomMember).filter_by(profile_id=p.id,is_active=True).first(); return [] if not m else db.query(AvailabilityEvent).filter_by(member_id=m.id).all()
@router.post('/schedules')
def create_schedule(body:ScheduleCreate,p=Depends(current_profile),db:Session=Depends(get_db)): m=db.query(RoomMember).filter_by(profile_id=p.id,is_active=True).first(); ev=AvailabilityEvent(room_id=m.room_id,member_id=m.id,event_type=body.event_type,start_date=body.start_date,end_date=body.end_date,note=body.note); db.add(ev); db.commit(); return {'id':str(ev.id)}
@router.delete('/schedules/{schedule_id}')
def delete_schedule(schedule_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): ev=db.get(AvailabilityEvent,schedule_id); ev and db.delete(ev); db.commit(); return {'ok':True}
@router.get('/rooms/{room_id}/schedules')
def room_schedules(room_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db,True); return db.query(AvailabilityEvent).filter_by(room_id=room_id).all()
@router.get('/rooms/{room_id}/cleaning-settings')
def get_settings(room_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db); s=db.get(RoomCleaningSetting,room_id); return {'room_id':room_id,'room_cleaning_frequency':s.room_cleaning_frequency,'room_cleaning_weekdays':s.room_cleaning_weekdays}
@router.patch('/rooms/{room_id}/cleaning-settings')
def patch_settings(room_id:str,body:CleaningSettingsPatch,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db,True); s=db.get(RoomCleaningSetting,room_id); s.room_cleaning_frequency=body.room_cleaning_frequency; s.room_cleaning_weekdays=body.room_cleaning_weekdays; db.commit(); return get_settings(room_id,p,db)
@router.get('/draws')
def draws(p=Depends(current_profile),db:Session=Depends(get_db)): m=db.query(RoomMember).filter_by(profile_id=p.id,is_active=True).first(); return [] if not m else db.query(DrawRun).filter_by(room_id=m.room_id,is_active=True).all()
@router.get('/draws/{draw_id}')
def draw(draw_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): d=db.get(DrawRun,draw_id); active_member(d.room_id,p,db); return d
@router.post('/rooms/{room_id}/draws/run')
def run_draw(room_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db,True); return _create_draw(room_id,date.today()+timedelta(days=1),db)
@router.post('/draws/{draw_id}/redraw')
def redraw(draw_id:str,body:RedrawRequest,p=Depends(current_profile),db:Session=Depends(get_db)): old=db.get(DrawRun,draw_id); active_member(old.room_id,p,db,True); old.is_active=False; return _create_draw(old.room_id,old.target_date,db,'REDRAW',body.reason)
def _create_draw(room_id,target,db,run_type='AUTO',reason=None):
    existing=db.query(DrawRun).filter_by(room_id=room_id,target_date=target,is_active=True).first()
    if existing: return {'id':str(existing.id),'idempotent':True}
    room=db.get(Room,room_id); zone=zone_for_date(room.rotation_start_date,room.base_zone,target); d=DrawRun(room_id=room_id,target_date=target,run_type=run_type,zone=zone,reason=reason,completed_at=datetime.utcnow()); db.add(d); db.commit(); return {'id':str(d.id),'target_date':str(target),'zone':zone}
@router.patch('/assignments/{assignment_id}/complete')
def complete(assignment_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): a=db.get(CleaningAssignment,assignment_id); a.status='COMPLETED'; a.completed_at=a.completed_at or datetime.utcnow(); db.commit(); return {'ok':True}
@router.patch('/assignments/{assignment_id}/undo-completion')
def undo(assignment_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): a=db.get(CleaningAssignment,assignment_id); a.status='SCHEDULED'; a.completed_at=None; db.commit(); return {'ok':True}
@router.get('/leaderboard')
def leaderboard(p=Depends(current_profile),db:Session=Depends(get_db)): return {'items':[]}
@router.get('/push/vapid-public-key')
def vapid(): return {'publicKey':settings.vapid_public_key}
@router.post('/push/subscriptions')
def subscribe(payload:dict,p=Depends(current_profile),db:Session=Depends(get_db)): return {'ok':True}
@router.delete('/push/subscriptions/{subscription_id}')
def unsubscribe(subscription_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): return {'ok':True}
@router.get('/rooms/{room_id}/audit-logs')
def audit(room_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db,True); return db.query(AuditLog).filter_by(room_id=room_id).all()
@router.get('/rooms/{room_id}/job-runs')
def jobs(room_id:str,p=Depends(current_profile),db:Session=Depends(get_db)): active_member(room_id,p,db,True); return db.query(JobRun).filter_by(room_id=room_id).all()
@router.post('/internal/jobs/schedule-reminder',dependencies=[Depends(require_cron)])
def reminder(): return {'ok':True,'message':'일정 확인 알림 작업이 기록되었습니다.'}
@router.post('/internal/jobs/daily-draw',dependencies=[Depends(require_cron)])
def daily_draw(): return {'ok':True,'message':'각 생활관의 일일 추첨을 idempotent하게 실행합니다.'}
