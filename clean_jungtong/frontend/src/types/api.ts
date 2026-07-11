export type Role='ADMIN'|'MEMBER';export type CleaningZone='RECYCLING'|'SHOWER_WASH_DRY'|'HALLWAY_STAIRS'|'DUTY_ROOM_PC_ROOM';export type ScheduleType='NIGHT_DUTY'|'LEAVE'|'OVERNIGHT'|'OUTING'|'EDUCATION'|'MEDICAL'|'MANUAL_EXCLUSION';
export interface Profile{id:string;email:string;display_name:string;active_room_id?:string;role?:Role}
export interface Room{id:string;name:string;timezone:string;draw_time:string;reminder_time:string;allow_same_person:boolean}
export interface ScheduleEvent{id:string;date:string;event_type:ScheduleType;note?:string}
export interface CleaningSettings{room_id:string;room_cleaning_frequency:number;room_cleaning_weekdays:number[];preview_text:string}
export interface DrawSummary{id:string;target_date:string;zone:CleaningZone;completed_at:string;tasks:{id:string;task_type:string;assignee_name?:string;status:string}[];exclusions:{member_name:string;reasons:string[]}[];stats:{active_members:number;excluded_members:number;candidate_members:number;task_count:number}}
