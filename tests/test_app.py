import pytest
from fastapi.testclient import TestClient
import base64
from PIL import Image
import io

from app import app

client = TestClient(app)

def _make_b64():
    img = Image.new("RGB", (1280, 720), color=(100, 150, 100))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

def test_start_session():
    res = client.post("/session/start", json={"venue": "東京", "race_number": "11"})
    assert res.status_code == 200
    assert "session_id" in res.json()

def test_analyze_frame_invalid_session():
    res = client.post("/analyze/frame", json={
        "session_id": "invalid", "image_base64": _make_b64(), "timestamp": 0.0
    })
    assert res.status_code == 404

def test_session_finish_invalid():
    res = client.post("/session/finish", json={"session_id": "invalid"})
    assert res.status_code == 404

def test_full_session_flow():
    res = client.post("/session/start", json={"venue": "中山", "race_number": "9"})
    sid = res.json()["session_id"]
    res = client.post("/session/finish", json={"session_id": sid})
    assert res.status_code == 200
    assert res.json()["status"] == "complete"
