from analyzer import parse_llava_response, _default_evaluation

def test_parse_valid_json():
    text = '''
    {
      "sabc": "A",
      "zenshin_kise": {"score": 10, "detail": "首リズム良好"},
      "front_drive": {"neck_rhythm": "良", "outside_walk": true, "catching_up": false},
      "condition": {"ear": "前向き", "sweat": "なし", "gait": "滑らか", "belly": "絞れ", "handlers": 1, "blinker": false},
      "body_type": {"tomo": "発達", "chest": "普通"},
      "course_fit": ["東京", "阪神"],
      "debuff_flag": false,
      "notes": "好気配"
    }
    '''
    result = parse_llava_response(text)
    assert result.sabc == "A"
    assert result.zenshin_kise.score == 10
    assert result.condition.sweat == "なし"
    assert result.condition.handlers == 1
    assert "東京" in result.course_fit

def test_parse_json_embedded_in_text():
    text = 'この馬の評価です。{"sabc": "S", "zenshin_kise": {"score": 15, "detail": "最高"}, "front_drive": {"neck_rhythm": "良", "outside_walk": true, "catching_up": true}, "condition": {"ear": "前向き", "sweat": "なし", "gait": "滑らか", "belly": "絞れ", "handlers": 1, "blinker": false}, "body_type": {"tomo": "発達", "chest": "普通"}, "course_fit": ["東京"], "debuff_flag": false, "notes": ""}'
    result = parse_llava_response(text)
    assert result.sabc == "S"

def test_parse_invalid_json_returns_default():
    result = parse_llava_response("画像が不明瞭です")
    assert result.sabc == "C"
    assert result.notes == "LLaVA解析失敗"

def test_default_evaluation():
    result = _default_evaluation()
    assert result.sabc == "C"
    assert result.debuff_flag is False
