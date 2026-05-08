import tempfile
from pathlib import Path
from models import SessionReport, HorseResult
from reporter import generate_html, save_report

def _make_report():
    horses = [
        HorseResult(horse_number=1, horse_name="テスト馬A", weight_change="+4kg",
                    jockey="川田", sabc="S", zenshin_kise_score=15, sweat="なし",
                    gait="滑らか", handlers=1, course_fit=["東京", "阪神"],
                    debuff_flag=False, notes="好気配", frame_count=8),
        HorseResult(horse_number=2, horse_name="テスト馬B", weight_change="-2kg",
                    jockey="戸崎", sabc="C", zenshin_kise_score=2, sweat="危険",
                    gait="硬め", handlers=2, course_fit=["中山"],
                    debuff_flag=True, notes="発汗危険", frame_count=5),
    ]
    return SessionReport(
        session_id="test01", venue="東京", race_number="11",
        date="20260601", horses=horses, total_frames=47
    )

def test_generate_html_contains_horse_names():
    report = _make_report()
    html = generate_html(report)
    assert "テスト馬A" in html
    assert "テスト馬B" in html

def test_generate_html_contains_sabc():
    html = generate_html(_make_report())
    assert "sabc-S" in html
    assert "sabc-C" in html

def test_generate_html_contains_debuff_warning():
    html = generate_html(_make_report())
    assert "注意馬" in html
    assert "テスト馬B" in html

def test_generate_html_contains_json():
    html = generate_html(_make_report())
    assert "paddock_agent" in html

def test_save_report_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = save_report(_make_report(), output_dir=tmpdir)
        assert Path(path).exists()
        assert path.endswith(".html")
