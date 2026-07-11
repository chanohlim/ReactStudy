import random
from dataclasses import dataclass
from .cleaning_rules import clamp_weight
@dataclass(frozen=True)
class Candidate: member_id:str; weight:float
@dataclass(frozen=True)
class CandidateSnapshot: member_id:str; weight:float; probability:float; selected:bool=False
def probabilities(candidates:list[Candidate])->list[CandidateSnapshot]:
    total=sum(max(c.weight,0.01) for c in candidates)
    return [CandidateSnapshot(c.member_id,c.weight,max(c.weight,0.01)/total) for c in candidates]
def weighted_pick(candidates:list[Candidate],rng:random.Random|None=None)->Candidate:
    if not candidates: raise ValueError('no candidates')
    rng=rng or random.Random(); total=sum(max(c.weight,0.01) for c in candidates); point=rng.random()*total; upto=0.0
    for c in candidates:
        upto+=max(c.weight,0.01)
        if upto>=point: return c
    return candidates[-1]
def increase_unselected(weight:float)->float: return clamp_weight(weight+0.05)
def completion_delta(task_type:str)->float: return {'ROOM':-0.10,'RECYCLING':-0.15,'HALLWAY_STAIRS':-0.15,'DUTY_ROOM_PC_ROOM':-0.20,'SHOWER_WASH_DRY':-0.25}.get(task_type,-0.10)
