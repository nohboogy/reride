from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel


class TrickDetection(BaseModel):
    trick_type: str
    confidence: float
    start_frame: int
    end_frame: int


class AnalysisResponse(BaseModel):
    id: int
    video_id: int
    tricks_detected: Optional[List[TrickDetection]]
    overall_score: Optional[float]
    difficulty_score: Optional[float]
    stability_score: Optional[float]
    feedback_text: Optional[List[str]]
    animation_url: Optional[str]
    highlight_url: Optional[str]
    overlay_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisStartRequest(BaseModel):
    style: str = "default"


class AnalysisStatusResponse(BaseModel):
    video_id: int
    status: str
    progress: int
