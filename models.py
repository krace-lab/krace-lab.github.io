from pydantic import BaseModel
from typing import Optional, List

class TelopsData(BaseModel):
    horse_number: Optional[int] = None
    horse_name: Optional[str] = None
    weight_change: Optional[str] = None
    load: Optional[float] = None
    jockey: Optional[str] = None

class ZenshinKise(BaseModel):
    score: int
    detail: str

class FrontDrive(BaseModel):
    neck_rhythm: str
    outside_walk: bool
    catching_up: bool

class Condition(BaseModel):
    ear: str
    sweat: str
    gait: str
    belly: str
    handlers: int
    blinker: bool

class BodyType(BaseModel):
    tomo: str
    chest: str

class FrameEvaluation(BaseModel):
    sabc: str
    zenshin_kise: ZenshinKise
    front_drive: FrontDrive
    condition: Condition
    body_type: BodyType
    course_fit: List[str]
    debuff_flag: bool
    notes: str

class FrameData(BaseModel):
    session_id: str
    image_base64: str
    timestamp: float = 0.0

class SessionStartRequest(BaseModel):
    venue: str = "東京"
    race_number: str = "11"

class SessionFinishRequest(BaseModel):
    session_id: str

class HorseResult(BaseModel):
    horse_number: int
    horse_name: str
    weight_change: str
    jockey: str
    sabc: str
    zenshin_kise_score: int
    sweat: str
    gait: str
    handlers: int
    course_fit: List[str]
    debuff_flag: bool
    notes: str
    frame_count: int

class SessionReport(BaseModel):
    session_id: str
    venue: str
    race_number: str
    date: str
    horses: List[HorseResult]
    total_frames: int
