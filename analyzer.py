import ollama
import json
import re
from models import FrameEvaluation, ZenshinKise, FrontDrive, Condition, BodyType

EVAL_PROMPT = """You are an expert Japanese horse racing analyst. Analyze this paddock image and respond with ONLY a JSON object, no other text.

Evaluation criteria:
- hindquarters development = suited for large turf courses (Tokyo/Hanshin/Chukyo/Niigata)
- chest/shoulder development = suited for dirt/small courses (Nakayama/Kyoto/Kokura/Hakodate/Sapporo/Fukushima)
- forward energy: head bobbing rhythm, walking outside track, chasing front horse
- ear position, gait, belly tightness, sweat (slight white OK / dripping = danger), handlers count, blinkers
- muscle tension, eye brightness, fighting spirit

Respond with exactly this JSON structure filled with your assessment:
{"sabc":"A","zenshin_kise":{"score":5,"detail":"good rhythm"},"front_drive":{"neck_rhythm":"良","outside_walk":false,"catching_up":false},"condition":{"ear":"前向き","sweat":"なし","gait":"滑らか","belly":"絞れ","handlers":1,"blinker":false},"body_type":{"tomo":"発達","chest":"普通"},"course_fit":["東京","阪神"],"debuff_flag":false,"notes":""}

sabc must be exactly one of: S, A, B, or C
zenshin_kise score must be an integer from -15 to 15"""

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
        sabc_raw = d.get("sabc", "C")
        sabc = sabc_raw if sabc_raw in ("S", "A", "B", "C") else "C"
        return FrameEvaluation(
            sabc=sabc,
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
