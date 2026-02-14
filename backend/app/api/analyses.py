"""
/api/v1/analyses — 업로드 + 분석을 하나로 묶은 통합 엔드포인트.
Flutter 클라이언트가 기대하는 API 형식과 일치시킴.
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

from app.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.storage import save_video, generate_filename, get_video_url
from app.services import VideoService, AnalysisService
from app.models.video import Video
from app.models.analysis import AnalysisResult

settings = get_settings()
router = APIRouter()


# ── Response schemas ─────────────────────────────────────────────────────────

class AnalysisResponse(BaseModel):
    id: str
    status: str  # pending | processing | done | failed
    video_id: int
    overall_score: Optional[float] = None
    difficulty_score: Optional[float] = None
    stability_score: Optional[float] = None
    feedback_text: Optional[str] = None
    tricks_detected: Optional[List[Any]] = None
    animation_url: Optional[str] = None
    highlight_url: Optional[str] = None
    overlay_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AnalysisListResponse(BaseModel):
    items: List[AnalysisResponse]
    total: int


# ── Helper ───────────────────────────────────────────────────────────────────

async def _build_response(video: Video, db: AsyncSession) -> AnalysisResponse:
    """Video + AnalysisResult → AnalysisResponse."""
    analysis_result = await db.execute(
        select(AnalysisResult).where(AnalysisResult.video_id == video.id)
    )
    analysis = analysis_result.scalar_one_or_none()

    # status mapping
    status_map = {
        "uploaded": "pending",
        "processing": "processing",
        "completed": "done",
        "failed": "failed",
    }
    status = status_map.get(video.status, "pending")

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

    return AnalysisResponse(
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
        created_at=video.created_at,
    )


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/", response_model=AnalysisResponse, status_code=201)
async def upload_and_analyze(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """영상 업로드 + 분석 자동 시작. Flutter 클라이언트 메인 엔드포인트."""
    # 파일 타입 검증
    if file.content_type not in settings.allowed_video_types:
        raise HTTPException(
            status_code=400,
            detail="지원하지 않는 영상 형식입니다 (MP4, MOV, AVI만 가능)"
        )

    content = await file.read()
    if len(content) > settings.max_video_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 {settings.max_video_size_mb}MB를 초과합니다"
        )

    # 저장 + DB 레코드 생성
    filename = generate_filename(file.filename or "video.mp4")
    storage_path = await save_video(content, filename)
    video = await VideoService.create_video(
        db=db,
        user_id=user_id,
        original_filename=file.filename or "video.mp4",
        storage_path=storage_path,
    )

    # 분석 자동 트리거 (백그라운드)
    asyncio.create_task(
        AnalysisService.run_analysis_sync(db, video.id)
    )
    video.status = "processing"
    await db.commit()

    return await _build_response(video, db)


@router.get("/", response_model=AnalysisListResponse)
async def list_analyses(
    skip: int = 0,
    limit: int = 20,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """현재 사용자의 분석 목록 반환."""
    videos, total = await VideoService.list_videos(
        db=db, user_id=user_id, skip=skip, limit=limit
    )
    items = [await _build_response(v, db) for v in videos]
    return AnalysisListResponse(items=items, total=total)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """특정 분석 결과 + 상태 조회."""
    try:
        video_id = int(analysis_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="분석을 찾을 수 없습니다")

    video = await VideoService.get_video(db=db, video_id=video_id, user_id=user_id)
    if not video:
        raise HTTPException(status_code=404, detail="분석을 찾을 수 없습니다")

    return await _build_response(video, db)
