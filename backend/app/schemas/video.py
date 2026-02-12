from datetime import datetime

from pydantic import BaseModel


class VideoResponse(BaseModel):
    id: int
    original_filename: str
    status: str
    duration_seconds: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class VideoListResponse(BaseModel):
    videos: list[VideoResponse]
    total: int
