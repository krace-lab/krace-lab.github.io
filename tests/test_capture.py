import base64
from PIL import Image
import io
from capture import preprocess_frame, is_stable_frame, crop_horse_area

def _make_test_image_b64(width=1280, height=720, color=(100, 150, 200)):
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

def test_preprocess_frame_returns_grayscale():
    b64 = _make_test_image_b64()
    result = preprocess_frame(b64)
    decoded = base64.b64decode(result)
    img = Image.open(io.BytesIO(decoded))
    assert img.mode == "L"  # grayscale
    assert img.width == 640

def test_preprocess_frame_reduces_resolution():
    b64 = _make_test_image_b64(1920, 1080)
    result = preprocess_frame(b64)
    decoded = base64.b64decode(result)
    img = Image.open(io.BytesIO(decoded))
    assert img.width == 640

def test_is_stable_frame_first_call():
    from capture import reset_prev_frame
    reset_prev_frame()
    b64 = _make_test_image_b64()
    assert is_stable_frame(b64) is True

def test_crop_horse_area_smaller_than_original():
    b64 = _make_test_image_b64(1280, 720)
    result = crop_horse_area(b64)
    decoded = base64.b64decode(result)
    img = Image.open(io.BytesIO(decoded))
    assert img.width < 1280
    assert img.height < 720
