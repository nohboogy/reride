from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.storage import get_video_url
from app.services import VideoService, AnalysisService
from app.schemas.analysis import AnalysisResponse, AnalysisStartRequest, AnalysisStatusResponse

router = APIRouter()


@router.get("/video/{video_id}", response_model=AnalysisResponse)
async def get_analysis(
    video_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get analysis result for a specific video."""
    # 영상 소유권 확인 (서비스 계층 사용)
    video = await VideoService.get_video(
        db=db,
        video_id=video_id,
        user_id=user_id
    )
    if not video:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")

    if video.status == "processing":
        raise HTTPException(status_code=202, detail="분석이 진행 중입니다")

    if video.status == "failed":
        raise HTTPException(
            status_code=500,
            detail="분석에 실패했습니다. 다시 시도해주세요"
        )

    # 분석 결과 조회 (서비스 계층 사용)
    analysis = await AnalysisService.get_analysis_result(
        db=db,
        video_id=video_id,
        user_id=user_id
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="분석 결과가 아직 없습니다")

    # URL 생성
    animation_url = None
    highlight_url = None
    overlay_url = None
    if analysis.animation_path:
        animation_url = await get_video_url(analysis.animation_path)
    if analysis.highlight_path:
        highlight_url = await get_video_url(analysis.highlight_path)
    if analysis.overlay_path:
        overlay_url = await get_video_url(analysis.overlay_path)

    return AnalysisResponse(
        id=analysis.id,
        video_id=analysis.video_id,
        tricks_detected=analysis.tricks_detected,
        overall_score=analysis.overall_score,
        difficulty_score=analysis.difficulty_score,
        stability_score=analysis.stability_score,
        feedback_text=analysis.feedback_text,
        animation_url=animation_url,
        highlight_url=highlight_url,
        overlay_url=overlay_url,
        created_at=analysis.created_at,
    )


@router.post("/video/{video_id}/start")
async def start_analysis(
    video_id: int,
    request: AnalysisStartRequest = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Start AI analysis for a video."""
    style = request.style if request else "default"
    try:
        result = await AnalysisService.request_analysis(
            db=db,
            video_id=video_id,
            user_id=user_id,
            style=style
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/video/{video_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    video_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get analysis progress status."""
    try:
        status = await AnalysisService.get_analysis_status(
            db=db,
            video_id=video_id,
            user_id=user_id
        )
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
