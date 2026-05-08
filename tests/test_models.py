from models import (
    TelopsData, FrameEvaluation, ZenshinKise,
    FrontDrive, Condition, BodyType, HorseResult, SessionReport
)

def test_telops_data_defaults():
    t = TelopsData()
    assert t.horse_number is None
    assert t.horse_name is None

def test_frame_evaluation_fields():
    e = FrameEvaluation(
        sabc="A",
        zenshin_kise=ZenshinKise(score=10, detail="良い"),
        front_drive=FrontDrive(neck_rhythm="良", outside_walk=True, catching_up=False),
        condition=Condition(ear="前向き", sweat="なし", gait="滑らか", belly="絞れ", handlers=1, blinker=False),
        body_type=BodyType(tomo="発達", chest="普通"),
        course_fit=["東京", "阪神"],
        debuff_flag=False,
        notes=""
    )
    assert e.sabc == "A"
    assert e.zenshin_kise.score == 10
    assert e.condition.handlers == 1

def test_horse_result_fields():
    h = HorseResult(
        horse_number=3, horse_name="テスト馬", weight_change="+4kg",
        jockey="川田", sabc="S", zenshin_kise_score=15, sweat="なし",
        gait="滑らか", handlers=1, course_fit=["東京"], debuff_flag=False,
        notes="", frame_count=8
    )
    assert h.horse_number == 3
    assert h.sabc == "S"
