import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from aggregator import aggregate_horse_frames
from analyzer import evaluate_frame
from capture import crop_horse_area, is_stable_frame, preprocess_frame
from models import (FrameData, SessionFinishRequest,
                    SessionReport, SessionStartRequest, TelopsData)
from ocr import extract_telops
from reporter import save_report

app = FastAPI(title="パドック診断API")
app.mount("/static", StaticFiles(directory="static"), name="static")

sessions: Dict[str, dict] = {}

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.post("/session/start")
def start_session(req: SessionStartRequest):
    sid = str(uuid.uuid4())[:8]
    sessions[sid] = {
        "venue": req.venue, "race_number": req.race_number,
        "horses": {}, "total_frames": 0,
        "pending": 0, "pending_lock": threading.Lock()
    }
    print(f"[START] session={sid} venue={req.venue} race={req.race_number}")
    return {"session_id": sid}

@app.post("/analyze/frame")
def analyze_frame(data: FrameData):
    session = sessions.get(data.session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "session not found"})

    session["total_frames"] += 1
    n = session["total_frames"]

    stable = is_stable_frame(data.image_base64)
    if not stable:
        if n % 10 == 0:
            print(f"[FRAME #{n}] skipped: motion")
        return {"status": "skipped", "reason": "motion"}

    telops = extract_telops(data.image_base64)
    horse_num = telops.horse_number
    print(f"[FRAME #{n}] stable=True  OCR→ horse_num={horse_num} name={telops.horse_name} weight={telops.weight_change}")

    if not horse_num:
        return {"status": "skipped", "reason": "no_horse_number"}

    horses = session["horses"]
    if horse_num not in horses:
        horses[horse_num] = {"telops": telops, "evals": [], "last_eval": 0}

    t = horses[horse_num]["telops"]
    if telops.horse_name:
        t.horse_name = telops.horse_name
    if telops.weight_change:
        t.weight_change = telops.weight_change
    if telops.jockey:
        t.jockey = telops.jockey

    elapsed = time.time() - horses[horse_num]["last_eval"]
    if elapsed < 15.0:
        print(f"[FRAME #{n}] horse={horse_num} rate_limit (elapsed={elapsed:.1f}s)")
        return {"status": "skipped", "reason": "rate_limit"}

    if session["pending"] >= 3:
        print(f"[FRAME #{n}] horse={horse_num} skipped: queue_full (pending={session['pending']})")
        return {"status": "skipped", "reason": "queue_full"}

    horses[horse_num]["last_eval"] = time.time()
    image_for_eval = preprocess_frame(crop_horse_area(data.image_base64))

    with session["pending_lock"]:
        session["pending"] += 1

    def run_eval(img, horse_entry, sess, h_num):
        print(f"[LLAVA] start eval horse={h_num}")
        evaluation = evaluate_frame(img)
        horse_entry["evals"].append(evaluation)
        with sess["pending_lock"]:
            sess["pending"] -= 1
        print(f"[LLAVA] done  horse={h_num} sabc={evaluation.sabc} pending={sess['pending']}")

    threading.Thread(
        target=run_eval,
        args=(image_for_eval, horses[horse_num], session, horse_num),
        daemon=True
    ).start()

    print(f"[FRAME #{n}] queued LLaVA for horse={horse_num} pending={session['pending']}")
    return {"status": "queued", "horse_number": horse_num}

@app.post("/session/finish")
def finish_session(req: SessionFinishRequest):
    session = sessions.get(req.session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "session not found"})

    print(f"[FINISH] session={req.session_id} total_frames={session['total_frames']} horses={list(session['horses'].keys())} pending={session['pending']}")

    # 実行中のLLaVA評価が終わるまで最大90秒待つ
    deadline = time.time() + 90
    while session["pending"] > 0 and time.time() < deadline:
        time.sleep(0.5)
    print(f"[FINISH] wait done, pending={session['pending']}")

    horses = [
        aggregate_horse_frames(num, d["telops"], d["evals"])
        for num, d in sorted(session["horses"].items())
    ]
    report = SessionReport(
        session_id=req.session_id, venue=session["venue"],
        race_number=session["race_number"],
        date=datetime.now().strftime("%Y%m%d"),
        horses=horses, total_frames=session["total_frames"]
    )
    Path("reports").mkdir(exist_ok=True)
    path = save_report(report, output_dir="reports")
    return {"status": "complete", "report_path": path, "report_id": req.session_id}

@app.get("/report/{filename}")
def get_report(filename: str):
    path = Path("reports") / filename
    if not path.exists():
        return JSONResponse(status_code=404, content={"error": "not found"})
    return FileResponse(str(path), media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
