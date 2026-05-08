from models import FrameEvaluation, ZenshinKise, FrontDrive, Condition, BodyType, TelopsData
from aggregator import aggregate_horse_frames

def _make_eval(sabc="A", score=10, sweat="なし", gait="滑らか", handlers=1,
               tomo="発達", chest="普通", debuff=False):
    return FrameEvaluation(
        sabc=sabc,
        zenshin_kise=ZenshinKise(score=score, detail=""),
        front_drive=FrontDrive(neck_rhythm="良", outside_walk=True, catching_up=False),
        condition=Condition(ear="前向き", sweat=sweat, gait=gait, belly="絞れ",
                            handlers=handlers, blinker=False),
        body_type=BodyType(tomo=tomo, chest=chest),
        course_fit=[],
        debuff_flag=debuff,
        notes=""
    )

def _telops(name="テスト馬", num=3):
    return TelopsData(horse_number=num, horse_name=name, weight_change="+4kg", jockey="川田")

def test_sabc_most_frequent():
    evals = [_make_eval("A"), _make_eval("A"), _make_eval("B")]
    result = aggregate_horse_frames(3, _telops(), evals)
    assert result.sabc == "A"

def test_zenshin_kise_average():
    evals = [_make_eval(score=10), _make_eval(score=12), _make_eval(score=11)]
    result = aggregate_horse_frames(3, _telops(), evals)
    assert result.zenshin_kise_score == 11

def test_sweat_danger_flag():
    evals = [_make_eval(sweat="なし"), _make_eval(sweat="危険"), _make_eval(sweat="なし")]
    result = aggregate_horse_frames(3, _telops(), evals)
    assert result.sweat == "危険"

def test_course_fit_tomo():
    evals = [_make_eval(tomo="発達", chest="普通")] * 3
    result = aggregate_horse_frames(3, _telops(), evals)
    assert "東京" in result.course_fit
    assert "阪神" in result.course_fit

def test_course_fit_chest():
    evals = [_make_eval(tomo="普通", chest="発達")] * 3
    result = aggregate_horse_frames(3, _telops(), evals)
    assert "中山" in result.course_fit

def test_debuff_any_frame():
    evals = [_make_eval(debuff=False), _make_eval(debuff=True), _make_eval(debuff=False)]
    result = aggregate_horse_frames(3, _telops(), evals)
    assert result.debuff_flag is True

def test_empty_evals():
    result = aggregate_horse_frames(3, _telops(), [])
    assert result.sabc == "C"
    assert result.frame_count == 0
