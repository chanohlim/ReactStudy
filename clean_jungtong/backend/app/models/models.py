import uuid
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, Time, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
def uid(): return uuid.uuid4()
class TimestampMixin:
    created_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at:Mapped[object]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
class Profile(Base,TimestampMixin):
    __tablename__='profiles'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); supabase_user_id:Mapped[str]=mapped_column(String(128),unique=True,index=True); email:Mapped[str]=mapped_column(String(320)); display_name:Mapped[str]=mapped_column(String(80)); is_active:Mapped[bool]=mapped_column(Boolean,default=True)
class Room(Base,TimestampMixin):
    __tablename__='rooms'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); name:Mapped[str]=mapped_column(String(80)); timezone:Mapped[str]=mapped_column(String(64),default='Asia/Seoul'); draw_time:Mapped[object]=mapped_column(Time); reminder_time:Mapped[object]=mapped_column(Time); rotation_start_date:Mapped[object]=mapped_column(Date); base_zone:Mapped[str]=mapped_column(String(40),default='RECYCLING'); allow_same_person:Mapped[bool]=mapped_column(Boolean,default=False); is_active:Mapped[bool]=mapped_column(Boolean,default=True)
class RoomMember(Base,TimestampMixin):
    __tablename__='room_members'; __table_args__=(UniqueConstraint('profile_id','is_active',name='uq_one_active_room_per_profile'),Index('ix_room_members_room_role','room_id','role'))
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); room_id=mapped_column(ForeignKey('rooms.id')); profile_id=mapped_column(ForeignKey('profiles.id')); role:Mapped[str]=mapped_column(String(16)); is_active:Mapped[bool]=mapped_column(Boolean,default=True); weight:Mapped[float]=mapped_column(Numeric(6,2),default=100); candidate_count:Mapped[int]=mapped_column(Integer,default=0); not_selected_count:Mapped[int]=mapped_column(Integer,default=0); incomplete_count:Mapped[int]=mapped_column(Integer,default=0)
class RoomInvite(Base,TimestampMixin):
    __tablename__='room_invites'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); room_id=mapped_column(ForeignKey('rooms.id'),index=True); created_by_member_id=mapped_column(ForeignKey('room_members.id')); token_hash:Mapped[str]=mapped_column(String(128),unique=True); expires_at=mapped_column(DateTime(timezone=True)); max_uses:Mapped[int]=mapped_column(Integer,default=1); used_count:Mapped[int]=mapped_column(Integer,default=0); revoked:Mapped[bool]=mapped_column(Boolean,default=False)
class AvailabilityEvent(Base,TimestampMixin):
    __tablename__='availability_events'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); room_id=mapped_column(ForeignKey('rooms.id'),index=True); member_id=mapped_column(ForeignKey('room_members.id'),index=True); event_type:Mapped[str]=mapped_column(String(40)); start_date=mapped_column(Date); end_date=mapped_column(Date); note:Mapped[str|None]=mapped_column(Text)
class RoomCleaningSetting(Base,TimestampMixin):
    __tablename__='room_cleaning_settings'; room_id=mapped_column(ForeignKey('rooms.id'),primary_key=True); room_cleaning_frequency:Mapped[int]=mapped_column(Integer,default=0); room_cleaning_weekdays:Mapped[list[int]]=mapped_column(ARRAY(Integer),default=list)
class WeeklyZoneOverride(Base,TimestampMixin):
    __tablename__='weekly_zone_overrides'; __table_args__=(UniqueConstraint('room_id','week_start_date'),); id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); room_id=mapped_column(ForeignKey('rooms.id')); week_start_date=mapped_column(Date); zone:Mapped[str]=mapped_column(String(40)); reason:Mapped[str|None]=mapped_column(Text)
class DrawRun(Base,TimestampMixin):
    __tablename__='draw_runs'; __table_args__=(UniqueConstraint('room_id','target_date','is_active',name='uq_active_draw_per_day'),); id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); room_id=mapped_column(ForeignKey('rooms.id'),index=True); target_date=mapped_column(Date,index=True); run_type:Mapped[str]=mapped_column(String(20),default='AUTO'); version:Mapped[int]=mapped_column(Integer,default=1); zone:Mapped[str]=mapped_column(String(40)); is_active:Mapped[bool]=mapped_column(Boolean,default=True); reason:Mapped[str|None]=mapped_column(Text); completed_at=mapped_column(DateTime(timezone=True))
class DrawTask(Base,TimestampMixin):
    __tablename__='draw_tasks'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); draw_run_id=mapped_column(ForeignKey('draw_runs.id'),index=True); task_type:Mapped[str]=mapped_column(String(40)); status:Mapped[str]=mapped_column(String(40),default='SCHEDULED'); duplicate_reason:Mapped[str|None]=mapped_column(Text)
class DrawCandidate(Base,TimestampMixin):
    __tablename__='draw_candidates'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); draw_run_id=mapped_column(ForeignKey('draw_runs.id'),index=True); member_id=mapped_column(ForeignKey('room_members.id')); weight_snapshot:Mapped[float]=mapped_column(Numeric(6,2)); probability_snapshot:Mapped[float]=mapped_column(Numeric(8,6)); selected:Mapped[bool]=mapped_column(Boolean,default=False)
class DrawExclusion(Base,TimestampMixin):
    __tablename__='draw_exclusions'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); draw_run_id=mapped_column(ForeignKey('draw_runs.id'),index=True); member_id=mapped_column(ForeignKey('room_members.id')); reasons:Mapped[list[str]]=mapped_column(ARRAY(String),default=list)
class CleaningAssignment(Base,TimestampMixin):
    __tablename__='cleaning_assignments'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); draw_task_id=mapped_column(ForeignKey('draw_tasks.id'),unique=True); member_id=mapped_column(ForeignKey('room_members.id'),nullable=True); status:Mapped[str]=mapped_column(String(40),default='SCHEDULED'); completed_at=mapped_column(DateTime(timezone=True),nullable=True); completed_by_member_id=mapped_column(ForeignKey('room_members.id'),nullable=True); weight_delta:Mapped[float]=mapped_column(Numeric(5,2),default=0)
class PushSubscription(Base,TimestampMixin):
    __tablename__='push_subscriptions'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); profile_id=mapped_column(ForeignKey('profiles.id')); endpoint:Mapped[str]=mapped_column(Text,unique=True); p256dh:Mapped[str]=mapped_column(Text); auth:Mapped[str]=mapped_column(Text); user_agent:Mapped[str|None]=mapped_column(Text); success_count:Mapped[int]=mapped_column(Integer,default=0); failure_count:Mapped[int]=mapped_column(Integer,default=0); is_active:Mapped[bool]=mapped_column(Boolean,default=True)
class AuditLog(Base,TimestampMixin):
    __tablename__='audit_logs'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); room_id=mapped_column(ForeignKey('rooms.id'),index=True); actor_member_id=mapped_column(ForeignKey('room_members.id'),nullable=True); action:Mapped[str]=mapped_column(String(80)); payload:Mapped[dict]=mapped_column(JSONB,default=dict)
class JobRun(Base,TimestampMixin):
    __tablename__='job_runs'; id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid); room_id=mapped_column(ForeignKey('rooms.id'),nullable=True,index=True); job_type:Mapped[str]=mapped_column(String(40)); status:Mapped[str]=mapped_column(String(40)); success_count:Mapped[int]=mapped_column(Integer,default=0); failure_count:Mapped[int]=mapped_column(Integer,default=0); error:Mapped[str|None]=mapped_column(Text)
