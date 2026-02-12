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
    tricks_detected: list[TrickDetection] | None
    overall_score: float | None
    difficulty_score: float | None
    stability_score: float | None
    feedback_text: list[str] | None
    animation_url: str | None
    highlight_url: str | None
    overlay_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisStartRequest(BaseModel):
    style: str = "default"


class AnalysisStatusResponse(BaseModel):
    video_id: int
    status: str
    progress: int
