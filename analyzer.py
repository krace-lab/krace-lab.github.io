import ollama
import json
import re
from models import FrameEvaluation, ZenshinKise, FrontDrive, Condition, BodyType

EVAL_PROMPT = """あなたは熟練の競馬相馬眼師です。馬体画像を分析し、必ずJSON形式のみで回答してください。

評価観点:
- トモ発達=芝大回り向き(東京・阪神・中京・新潟) / 胸前発達=ダート小回り向き(中山・京都・小倉・函館・札幌・福島)
- 前進気勢: 首の上下リズム・外側歩行・前馬追走
- 耳の向き・歩様・お腹の絞り・発汗(うっすら白汗OK/垂れる=危険)・引き手人数・ブリンカー有無
- 筋肉の張り・目の輝き・勝負気配

{"sabc":"S/A/B/C","zenshin_kise":{"score":-15から15,"detail":""},"front_drive":{"neck_rhythm":"良/普通/悪","outside_walk":true/false,"catching_up":true/false},"condition":{"ear":"前向き/普通/後ろ","sweat":"なし/うっすら/危険","gait":"滑らか/普通/硬め","belly":"絞れ/普通/太め","handlers":1または2,"blinker":true/false},"body_type":{"tomo":"発達/普通/未発達","chest":"発達/普通/未発達"},"course_fit":[],"debuff_flag":true/false,"notes":""}"""

def evaluate_frame(image_base64: str, model: str = "llava:7b") -> FrameEvaluation:
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": EVAL_PROMPT, "images": [image_base64]}]
    )
    return parse_llava_response(response["message"]["content"])

def parse_llava_response(text: str) -> FrameEvaluation:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return _default_evaluation()
    try:
        d = json.loads(match.group())
        return FrameEvaluation(
            sabc=d.get("sabc", "C"),
            zenshin_kise=ZenshinKise(**d.get("zenshin_kise", {"score": 0, "detail": ""})),
            front_drive=FrontDrive(**d.get("front_drive", {"neck_rhythm": "普通", "outside_walk": False, "catching_up": False})),
            condition=Condition(**d.get("condition", {"ear": "普通", "sweat": "なし", "gait": "普通", "belly": "普通", "handlers": 1, "blinker": False})),
            body_type=BodyType(**d.get("body_type", {"tomo": "普通", "chest": "普通"})),
            course_fit=d.get("course_fit", []),
            debuff_flag=d.get("debuff_flag", False),
            notes=d.get("notes", "")
        )
    except (json.JSONDecodeError, KeyError, TypeError):
        return _default_evaluation()

def _default_evaluation() -> FrameEvaluation:
    return FrameEvaluation(
        sabc="C",
        zenshin_kise=ZenshinKise(score=0, detail="解析失敗"),
        front_drive=FrontDrive(neck_rhythm="普通", outside_walk=False, catching_up=False),
        condition=Condition(ear="普通", sweat="なし", gait="普通", belly="普通", handlers=1, blinker=False),
        body_type=BodyType(tomo="普通", chest="普通"),
        course_fit=[],
        debuff_flag=False,
        notes="LLaVA解析失敗"
    )
