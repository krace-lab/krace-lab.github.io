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
        "horses": {}, "total_frames": 0
    }
    return {"session_id": sid}

@app.post("/analyze/frame")
def analyze_frame(data: FrameData):
    session = sessions.get(data.session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "session not found"})

    session["total_frames"] += 1

    if not is_stable_frame(data.image_base64):
        return {"status": "skipped", "reason": "motion"}

    telops = extract_telops(data.image_base64)
    horse_num = telops.horse_number
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

    if time.time() - horses[horse_num]["last_eval"] < 4.0:
        return {"status": "skipped", "reason": "rate_limit"}

    evaluation = evaluate_frame(preprocess_frame(crop_horse_area(data.image_base64)))
    horses[horse_num]["evals"].append(evaluation)
    horses[horse_num]["last_eval"] = time.time()

    return {"status": "evaluated", "horse_number": horse_num,
            "sabc": evaluation.sabc, "zenshin_kise": evaluation.zenshin_kise.score}

@app.post("/session/finish")
def finish_session(req: SessionFinishRequest):
    session = sessions.get(req.session_id)
    if not session:
        return JSONResponse(status_code=404, content={"error": "session not found"})

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
