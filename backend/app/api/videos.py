from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.storage import save_video, generate_filename
from app.services import VideoService
from app.schemas.video import VideoResponse, VideoListResponse

settings = get_settings()
router = APIRouter()


@router.post("/upload", response_model=VideoResponse, status_code=201)
async def upload_video(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Upload a new video file."""
    # 파일 타입 검증
    if file.content_type not in settings.allowed_video_types:
        raise HTTPException(
            status_code=400,
            detail="지원하지 않는 영상 형식입니다 (MP4, MOV, AVI만 가능)"
        )

    # 파일 크기 검증
    content = await file.read()
    if len(content) > settings.max_video_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 {settings.max_video_size_mb}MB를 초과합니다"
        )

    # 파일 저장
    filename = generate_filename(file.filename or "video.mp4")
    storage_path = await save_video(content, filename)

    # DB 레코드 생성 (서비스 계층 사용)
    video = await VideoService.create_video(
        db=db,
        user_id=user_id,
        original_filename=file.filename or "video.mp4",
        storage_path=storage_path
    )

    # TODO: Celery 태스크로 AI 분석 비동기 실행
    # from app.workers.analyze_video import analyze_video_task
    # analyze_video_task.delay(video.id)

    return video


@router.get("/", response_model=VideoListResponse)
async def list_videos(
    skip: int = 0,
    limit: int = 20,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all videos for the current user with pagination."""
    videos, total = await VideoService.list_videos(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    return VideoListResponse(videos=videos, total=total)


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific video by ID."""
    video = await VideoService.get_video(
        db=db,
        video_id=video_id,
        user_id=user_id
    )
    if not video:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")
    return video


@router.delete("/{video_id}", status_code=204)
async def delete_video(
    video_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a video and its associated analysis."""
    deleted = await VideoService.delete_video(
        db=db,
        video_id=video_id,
        user_id=user_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="영상을 찾을 수 없습니다")
    return None
