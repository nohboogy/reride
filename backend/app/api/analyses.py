"""Unified /api/v1/analyses endpoint.

POST /   – upload video + auto-trigger analysis
GET  /   – list analyses for the current user
GET  /{id} – get analysis status / result (ID = video_id as string)
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.storage import generate_filename, get_video_url, save_video
from app.models.analysis import AnalysisResult
from app.models.video import Video
from app.services import AnalysisService, VideoService

settings = get_settings()
router = APIRouter()


# ── Response schemas ─────────────────────────────────────────────────────────


class AnalysisCreateResponse(BaseModel):
    id: str
    status: str
    video_id: int
    created_at: datetime


class AnalysisDetailResponse(BaseModel):
    id: str
    status: str
    video_id: int
    overall_score: Optional[float] = None
    difficulty_score: Optional[float] = None
    stability_score: Optional[float] = None
    feedback_text: Optional[Any] = None
    tricks_detected: Optional[Any] = None
    animation_url: Optional[str] = None
    highlight_url: Optional[str] = None
    overlay_url: Optional[str] = None
    created_at: datetime


class AnalysisListResponse(BaseModel):
    items: list[AnalysisDetailResponse]
    total: int


# ── Helper ───────────────────────────────────────────────────────────────────

# Backend video status → analysis status mapping
_STATUS_MAP = {
    "uploaded": "pending",
    "processing": "processing",
    "completed": "done",
    "failed": "failed",
}


async def _build_detail_response(
    video: Video,
    analysis: Optional[AnalysisResult],
) -> AnalysisDetailResponse:
    """Construct an AnalysisDetailResponse from a Video + optional AnalysisResult."""
    status = _STATUS_MAP.get(video.status, video.status)
    created_at = analysis.created_at if analysis else video.created_at

    animation_url = None
    highlight_url = None
    overlay_url = None
    if analysis:
        if analysis.animation_path:
            animation_url = await get_video_url(analysis.animation_path)
        if analysis.highlight_path:
            highlight_url = await get_video_url(analysis.highlight_path)
        if analysis.overlay_path:
            overlay_url = await get_video_url(analysis.overlay_path)

    return AnalysisDetailResponse(
        id=str(video.id),
        status=status,
        video_id=video.id,
        overall_score=analysis.overall_score if analysis else None,
        difficulty_score=analysis.difficulty_score if analysis else None,
        stability_score=analysis.stability_score if analysis else None,
        feedback_text=analysis.feedback_text if analysis else None,
        tricks_detected=analysis.tricks_detected if analysis else None,
        animation_url=animation_url,
        highlight_url=highlight_url,
        overlay_url=overlay_url,
        created_at=created_at,
    )


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.post("", response_model=AnalysisCreateResponse, status_code=201)
async def create_analysis(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Upload a video file and automatically trigger AI analysis."""
    # Validate file type
    if file.content_type not in settings.allowed_video_types:
        raise HTTPException(
            status_code=400,
            detail="지원하지 않는 영상 형식입니다 (MP4, MOV, AVI만 가능)",
        )

    # Read content and validate size
    content = await file.read()
    if len(content) > settings.max_video_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 {settings.max_video_size_mb}MB를 초과합니다",
        )

    # Save video to storage (local or S3)
    filename = generate_filename(file.filename or "video.mp4")
    storage_path = await save_video(content, filename)

    # Create Video DB record
    video = await VideoService.create_video(
        db=db,
        user_id=user_id,
        original_filename=file.filename or "video.mp4",
        storage_path=storage_path,
    )

    # Auto-trigger analysis (non-blocking in async mode)
    await AnalysisService.request_analysis(
        db=db,
        video_id=video.id,
        user_id=user_id,
    )

    return AnalysisCreateResponse(
        id=str(video.id),
        status="processing",
        video_id=video.id,
        created_at=video.created_at,
    )


@router.get("", response_model=AnalysisListResponse)
async def list_analyses(
    skip: int = 0,
    limit: int = 20,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all analyses (videos) for the current user with pagination."""
    # Total count
    count_stmt = select(func.count()).select_from(Video).where(
        Video.user_id == user_id
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Paginated video list ordered by newest first
    stmt = (
        select(Video)
        .where(Video.user_id == user_id)
        .order_by(Video.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    videos = result.scalars().all()

    items = []
    for video in videos:
        analysis_result = await db.execute(
            select(AnalysisResult).where(AnalysisResult.video_id == video.id)
        )
        analysis = analysis_result.scalar_one_or_none()
        items.append(await _build_detail_response(video, analysis))

    return AnalysisListResponse(items=items, total=total)


@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
async def get_analysis(
    analysis_id: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get analysis status and result by ID (ID = video_id as string)."""
    try:
        video_id = int(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="유효하지 않은 분석 ID입니다")

    # Fetch video with ownership check
    video = await VideoService.get_video(db=db, video_id=video_id, user_id=user_id)
    if not video:
        raise HTTPException(status_code=404, detail="분석을 찾을 수 없습니다")

    # Fetch analysis result (may not exist yet if still processing)
    analysis_result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.video_id == video_id)
    )
    analysis = analysis_result.scalar_one_or_none()

    return await _build_detail_response(video, analysis)
