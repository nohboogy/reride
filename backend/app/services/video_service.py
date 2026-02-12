from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from app.models.video import Video
from app.models.analysis import AnalysisResult
from pathlib import Path
import os
import uuid
import aiofiles


class VideoService:
    # Max file size 100MB
    MAX_FILE_SIZE = 100 * 1024 * 1024
    ALLOWED_TYPES = ["video/mp4", "video/quicktime", "video/x-msvideo"]

    @staticmethod
    async def create_video(
        db: AsyncSession,
        user_id: int,
        original_filename: str,
        storage_path: str
    ) -> Video:
        """Create Video DB record (file already saved by caller)."""
        video = Video(
            user_id=user_id,
            original_filename=original_filename,
            storage_path=storage_path,
            status="uploaded"
        )
        db.add(video)
        await db.commit()
        await db.refresh(video)
        return video

    @staticmethod
    async def upload_video(
        db: AsyncSession,
        user_id: int,
        file_content: bytes,
        filename: str,
        content_type: str,
        storage_dir: str = "uploads"
    ) -> Video:
        """Validate file, save to storage, create DB record."""
        # Validate file type and size
        is_valid, error_msg = VideoService.validate_video_file(file_content, content_type)
        if not is_valid:
            raise ValueError(error_msg)

        # Generate unique storage path
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        storage_path = Path(storage_dir) / unique_filename

        # Create storage directory if it doesn't exist
        storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Save file
        async with aiofiles.open(str(storage_path), 'wb') as f:
            await f.write(file_content)

        # Create Video record
        video = Video(
            user_id=user_id,
            original_filename=filename,
            storage_path=str(storage_path),
            status="uploaded"
        )
        db.add(video)
        await db.commit()
        await db.refresh(video)

        return video

    @staticmethod
    async def get_video(
        db: AsyncSession,
        video_id: int,
        user_id: int
    ) -> Video | None:
        """Fetch single video with ownership check."""
        stmt = select(Video).where(
            Video.id == video_id,
            Video.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_videos(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[Video], int]:
        """Paginated video list with total count."""
        # Get total count
        count_stmt = select(func.count()).select_from(Video).where(
            Video.user_id == user_id
        )
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()

        # Get paginated videos
        stmt = (
            select(Video)
            .where(Video.user_id == user_id)
            .order_by(Video.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        videos = result.scalars().all()

        return list(videos), total

    @staticmethod
    async def delete_video(
        db: AsyncSession,
        video_id: int,
        user_id: int
    ) -> bool:
        """Delete video and associated files."""
        # Check ownership
        video = await VideoService.get_video(db, video_id, user_id)
        if not video:
            return False

        # Delete analysis result if exists
        delete_analysis_stmt = delete(AnalysisResult).where(
            AnalysisResult.video_id == video_id
        )
        await db.execute(delete_analysis_stmt)

        # Delete files from storage
        try:
            if os.path.exists(video.storage_path):
                os.remove(video.storage_path)
        except Exception:
            # Log error but continue with DB deletion
            pass

        # Delete DB record
        await db.delete(video)
        await db.commit()

        return True

    @staticmethod
    def validate_video_file(
        content: bytes,
        content_type: str
    ) -> tuple[bool, str]:
        """Validate file type and size. Returns (is_valid, error_message)."""
        # Check file size
        if len(content) > VideoService.MAX_FILE_SIZE:
            return False, f"File size exceeds maximum allowed size of {VideoService.MAX_FILE_SIZE / 1024 / 1024}MB"

        # Check content type
        if content_type not in VideoService.ALLOWED_TYPES:
            return False, f"File type {content_type} not allowed. Allowed types: {', '.join(VideoService.ALLOWED_TYPES)}"

        return True, ""
