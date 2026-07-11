from datetime import date,timedelta
ZONES=['RECYCLING','SHOWER_WASH_DRY','HALLWAY_STAIRS','DUTY_ROOM_PC_ROOM']; DELTAS={'ROOM':-0.10,'RECYCLING':-0.15,'HALLWAY_STAIRS':-0.15,'DUTY_ROOM_PC_ROOM':-0.20,'SHOWER_WASH_DRY':-0.25}
def clamp_weight(w:float)->float: return max(99.0,min(101.0,round(w,2)))
def week_start(d:date)->date: return d-timedelta(days=d.weekday())
def zone_for_date(start:date,base_zone:str,target:date,override:str|None=None)->str:
    if override: return override
    diff=(week_start(target)-week_start(start)).days//7
    return ZONES[(ZONES.index(base_zone)+diff)%len(ZONES)]
def validate_room_cleaning(freq:int,weekdays:list[int])->bool:
    if freq==0: return weekdays==[]
    if freq==7: return sorted(weekdays)==list(range(7))
    return 1<=freq<=6 and len(set(weekdays))==freq and all(0<=d<=6 for d in weekdays)
