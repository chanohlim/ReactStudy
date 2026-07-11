from datetime import date
import random
from app.services.cleaning_rules import clamp_weight, validate_room_cleaning, zone_for_date
from app.services.draw_engine import Candidate, probabilities, weighted_pick, increase_unselected, completion_delta

def test_zone_rotation():
    assert zone_for_date(date(2026,7,6),'RECYCLING',date(2026,7,13))=='SHOWER_WASH_DRY'

def test_cleaning_validation():
    assert validate_room_cleaning(2,[1,5])
    assert not validate_room_cleaning(2,[1])
    assert validate_room_cleaning(7,[0,1,2,3,4,5,6])

def test_weights():
    assert clamp_weight(98)==99.0
    assert increase_unselected(100)==100.05
    assert completion_delta('SHOWER_WASH_DRY')==-0.25

def test_weighted_pick_seeded():
    cs=[Candidate('a',100),Candidate('b',101)]
    assert sum(p.probability for p in probabilities(cs)) == 1
    assert weighted_pick(cs, random.Random(1)).member_id in {'a','b'}
