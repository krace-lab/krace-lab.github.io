from ocr import parse_telop_text

def test_parse_horse_number():
    result = parse_telop_text("3 テスト馬 54.0 +4kg 川田")
    assert result.horse_number == 3

def test_parse_weight_change_positive():
    result = parse_telop_text("5 ダービー馬 56.0 +6kg 武豊")
    assert result.weight_change == "+6kg"

def test_parse_weight_change_negative():
    result = parse_telop_text("10 サンプル -2kg 57.0 横山武")
    assert result.weight_change == "-2kg"

def test_parse_weight_change_zero():
    result = parse_telop_text("1 テスト 0kg 54.0 戸崎")
    assert result.weight_change == "0kg"

def test_parse_load():
    result = parse_telop_text("7 テスト馬 55.0 +4kg 福永")
    assert result.load == 55.0

def test_parse_empty_text():
    result = parse_telop_text("")
    assert result.horse_number is None
    assert result.weight_change is None
