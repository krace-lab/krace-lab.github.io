import re
from models import TelopsData

_reader = None

def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["ja", "en"], gpu=False)
    return _reader

def extract_telops(image_base64: str) -> TelopsData:
    import numpy as np
    from PIL import Image
    import io
    import base64

    image = Image.open(io.BytesIO(base64.b64decode(image_base64)))
    w, h = image.size
    telop = image.crop((0, int(h * 0.75), w, h))
    results = _get_reader().readtext(np.array(telop))
    text = " ".join(r[1] for r in results)
    print(f"[OCR] image={w}x{h}  raw_text='{text}'")
    return parse_telop_text(text)

def parse_telop_text(text: str) -> TelopsData:
    data = TelopsData()

    num = re.search(r"(?<!\d)([1-9]|1[0-8])(?!\d)", text)
    if num:
        data.horse_number = int(num.group(1))

    weight = re.search(r"([+-]?\d+)kg", text)
    if weight:
        data.weight_change = weight.group(0)

    load = re.search(r"(\d{2}\.\d)", text)
    if load:
        data.load = float(load.group(1))

    return data
