from collections import Counter
from typing import List
from models import FrameEvaluation, HorseResult, TelopsData

_COURSE_MAP = {
    "tomo": ["東京", "阪神", "中京", "新潟"],
    "chest": ["中山", "京都", "小倉", "函館", "札幌", "福島"]
}

def aggregate_horse_frames(
    horse_number: int,
    telops: TelopsData,
    evaluations: List[FrameEvaluation]
) -> HorseResult:
    if not evaluations:
        return _empty_result(horse_number, telops)

    sabc = Counter(e.sabc for e in evaluations).most_common(1)[0][0]
    avg_score = int(sum(e.zenshin_kise.score for e in evaluations) / len(evaluations))

    sweat_vals = [e.condition.sweat for e in evaluations]
    sweat = "危険" if "危険" in sweat_vals else ("うっすら" if "うっすら" in sweat_vals else "なし")

    gait = Counter(e.condition.gait for e in evaluations).most_common(1)[0][0]
    handlers = Counter(e.condition.handlers for e in evaluations).most_common(1)[0][0]

    tomo = Counter(e.body_type.tomo for e in evaluations).most_common(1)[0][0]
    chest = Counter(e.body_type.chest for e in evaluations).most_common(1)[0][0]
    course_fit = []
    if tomo == "発達":
        course_fit.extend(_COURSE_MAP["tomo"])
    if chest == "発達":
        course_fit.extend(_COURSE_MAP["chest"])
    if not course_fit:
        all_courses = [c for e in evaluations for c in e.course_fit]
        course_fit = [c for c, _ in Counter(all_courses).most_common(3)]

    debuff = any(e.debuff_flag for e in evaluations)
    notes = "、".join({e.notes for e in evaluations if e.notes and e.notes != "LLaVA解析失敗"})

    return HorseResult(
        horse_number=horse_number,
        horse_name=telops.horse_name or f"馬番{horse_number}",
        weight_change=telops.weight_change or "不明",
        jockey=telops.jockey or "不明",
        sabc=sabc,
        zenshin_kise_score=avg_score,
        sweat=sweat,
        gait=gait,
        handlers=handlers,
        course_fit=list(set(course_fit)),
        debuff_flag=debuff,
        notes=notes,
        frame_count=len(evaluations)
    )

def _empty_result(horse_number: int, telops: TelopsData) -> HorseResult:
    return HorseResult(
        horse_number=horse_number,
        horse_name=telops.horse_name or f"馬番{horse_number}",
        weight_change=telops.weight_change or "不明",
        jockey=telops.jockey or "不明",
        sabc="C", zenshin_kise_score=0, sweat="なし",
        gait="普通", handlers=1, course_fit=[],
        debuff_flag=False, notes="フレームなし", frame_count=0
    )
