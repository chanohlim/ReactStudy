from datetime import date,datetime,time
from pydantic import BaseModel,Field,field_validator
from app.services.cleaning_rules import validate_room_cleaning
class ProfileOut(BaseModel): id:str; email:str; display_name:str
class ProfilePatch(BaseModel): display_name:str=Field(min_length=1,max_length=80)
class RoomCreate(BaseModel): name:str=Field(min_length=1,max_length=80); timezone:str='Asia/Seoul'; draw_time:time=time(21,0); reminder_time:time=time(20,50); allow_same_person:bool=False
class RoomOut(RoomCreate): id:str
class InviteCreate(BaseModel): expires_at:datetime; max_uses:int=Field(default=1,ge=1,le=100)
class InviteOut(BaseModel): id:str; invite_url:str; expires_at:datetime; max_uses:int; used_count:int
class ScheduleCreate(BaseModel): event_type:str; start_date:date; end_date:date; note:str|None=None
class CleaningSettingsPatch(BaseModel):
    room_cleaning_frequency:int=Field(ge=0,le=7)
    room_cleaning_weekdays:list[int]
    @field_validator('room_cleaning_weekdays')
    @classmethod
    def valid_days(cls,v,info):
        freq=info.data.get('room_cleaning_frequency')
        if freq is not None and not validate_room_cleaning(freq,v): raise ValueError('빈도와 요일 수가 일치하지 않습니다.')
        return v
class RedrawRequest(BaseModel): reason:str=Field(min_length=1)
