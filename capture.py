import numpy as np
from PIL import Image
import io
import base64

_prev_frame = None

def reset_prev_frame():
    global _prev_frame
    _prev_frame = None

def preprocess_frame(image_base64: str) -> str:
    image = _decode(image_base64)
    w, h = image.size
    new_h = int(h * 640 / w)
    image = image.resize((640, new_h)).convert("L")
    return _encode(image)

def is_stable_frame(image_base64: str, low: float = 0.003, high: float = 0.04) -> bool:
    global _prev_frame
    image = _decode(image_base64).convert("L").resize((320, 180))
    frame = np.array(image, dtype=np.float32) / 255.0
    if _prev_frame is None:
        _prev_frame = frame
        return True
    diff = np.mean(np.abs(frame - _prev_frame))
    _prev_frame = frame
    return low < diff < high

def crop_horse_area(image_base64: str) -> str:
    image = _decode(image_base64)
    w, h = image.size
    cropped = image.crop((int(w * 0.1), int(h * 0.05), int(w * 0.9), int(h * 0.82)))
    return _encode(cropped)

def _decode(image_base64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(image_base64)))

def _encode(image: Image.Image, quality: int = 85) -> str:
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode()
