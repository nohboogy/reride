"""영상 분석 서비스."""

import asyncio
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.video import Video
from app.models.analysis import AnalysisResult
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Only import Celery if enabled
if settings.use_celery:
    try:
        from celery.result import AsyncResult
        from app.workers.analyze_video import analyze_video_task
    except ImportError:
        logger.warning("Celery not available, using sync mode")


class AnalysisService:
    """영상 분석 요청 및 상태 관리 서비스."""

    @staticmethod
    async def run_analysis_sync(db: AsyncSession, video_id: int, style: str = "default"):
        """Run analysis synchronously (without Celery) for local dev."""
        def _run_pipeline(video_path, vid_id, style_param):
            import sys
            project_root = Path(__file__).parent.parent.parent.parent
            sys.path.insert(0, str(project_root))
            from ai.pipeline import ReridePipeline
            with ReridePipeline(output_dir="outputs") as pipeline:
                return pipeline.analyze(video_path=video_path, video_id=str(vid_id), style=style_param)

        # Get video
        result = await db.execute(select(Video).where(Video.id == video_id))
        video = result.scalar_one()

        # Run AI pipeline in thread
        pipeline_result = await asyncio.to_thread(_run_pipeline, video.storage_path, video_id, style)

        # Save results
        analysis = AnalysisResult(
            video_id=video_id,
            tricks_detected=[{
                "trick_type": t.trick_type,
                "confidence": t.confidence,
                "start_frame": t.start_frame,
                "end_frame": t.end_frame
            } for t in pipeline_result.tricks],
            overall_score=pipeline_result.scores.overall_score,
            difficulty_score=pipeline_result.scores.difficulty_score,
            stability_score=pipeline_result.scores.stability_score,
            feedback_text=pipeline_result.scores.feedback,
            animation_path=pipeline_result.animation_path,
            highlight_path=pipeline_result.highlight_path,
            overlay_path=pipeline_result.overlay_path,
            pose_data_path=pipeline_result.pose_data_path,
        )
        db.add(analysis)
        video.status = "completed"
        await db.commit()
        logger.info(f"분석 완료: video_id={video_id}")

    @staticmethod
    async def request_analysis(
        db: AsyncSession,
        video_id: int,
        user_id: int,
        style: str = "default"
    ) -> dict:
        """
        영상 분석 시작 (Celery 또는 동기 모드).

        Args:
            db: 비동기 데이터베이스 세션
            video_id: 분석할 영상 ID
            user_id: 요청 사용자 ID
            style: 분석 스타일 (default, detailed 등)

        Returns:
            {"task_id": str, "status": "queued", "video_id": int}

        Raises:
            ValueError: 영상을 찾을 수 없거나 권한이 없을 때
        """
        # 영상 조회 및 소유권 확인
        result = await db.execute(
            select(Video).where(Video.id == video_id, Video.user_id == user_id)
        )
        video = result.scalar_one_or_none()

        if not video:
            raise ValueError("영상을 찾을 수 없거나 접근 권한이 없습니다.")

        # 이미 처리 중인지 확인
        if video.status == "processing":
            raise ValueError("영상이 이미 분석 중입니다.")

        # 영상 상태를 processing으로 업데이트
        video.status = "processing"
        await db.commit()

        if settings.use_celery:
            # Celery 태스크 큐에 추가
            task = analyze_video_task.delay(video_id, style)
            logger.info(f"분석 태스크 큐 등록: video_id={video_id}, task_id={task.id}")
            return {
                "task_id": task.id,
                "status": "queued",
                "video_id": video_id
            }
        else:
            # Run in background without blocking
            asyncio.create_task(AnalysisService.run_analysis_sync(db, video_id, style))
            logger.info(f"분석 시작 (동기 모드): video_id={video_id}")
            return {
                "task_id": f"sync-{video_id}",
                "status": "processing",
                "video_id": video_id
            }

    @staticmethod
    async def get_analysis_status(
        db: AsyncSession,
        video_id: int,
        user_id: int
    ) -> dict:
        """
        영상 분석 상태 및 진행률 조회.

        Args:
            db: 비동기 데이터베이스 세션
            video_id: 영상 ID
            user_id: 요청 사용자 ID

        Returns:
            {
                "video_id": int,
                "status": str,  # uploaded, queued, processing, completed, failed
                "progress": int  # 0-100
            }

        Raises:
            ValueError: 영상을 찾을 수 없거나 권한이 없을 때
        """
        # 영상 조회 및 소유권 확인
        result = await db.execute(
            select(Video).where(Video.id == video_id, Video.user_id == user_id)
        )
        video = result.scalar_one_or_none()

        if not video:
            raise ValueError("영상을 찾을 수 없거나 접근 권한이 없습니다.")

        status_info = {
            "video_id": video_id,
            "status": video.status,
            "progress": 0
        }

        # 상태별 진행률 설정
        if video.status == "completed":
            status_info["progress"] = 100
        elif video.status == "processing":
            # Celery 태스크 정보를 조회하여 진행률 계산
            # 현재는 단순히 50%로 설정 (실제 구현 시 태스크 메타데이터 사용)
            status_info["progress"] = 50
        elif video.status == "failed":
            status_info["progress"] = 0
        elif video.status == "uploaded":
            status_info["progress"] = 0

        return status_info

    @staticmethod
    async def get_analysis_result(
        db: AsyncSession,
        video_id: int,
        user_id: int
    ) -> AnalysisResult | None:
        """
        완료된 영상 분석 결과 조회.

        Args:
            db: 비동기 데이터베이스 세션
            video_id: 영상 ID
            user_id: 요청 사용자 ID

        Returns:
            AnalysisResult 객체 또는 None (결과가 없을 경우)

        Raises:
            ValueError: 영상을 찾을 수 없거나 권한이 없을 때
        """
        # 영상 소유권 확인
        result = await db.execute(
            select(Video).where(Video.id == video_id, Video.user_id == user_id)
        )
        video = result.scalar_one_or_none()

        if not video:
            raise ValueError("영상을 찾을 수 없거나 접근 권한이 없습니다.")

        # 분석 결과 조회
        result = await db.execute(
            select(AnalysisResult).where(AnalysisResult.video_id == video_id)
        )
        analysis = result.scalar_one_or_none()

        return analysis

    @staticmethod
    def cancel_analysis(task_id: str) -> bool:
        """
        실행 중인 Celery 태스크 취소.

        Args:
            task_id: Celery 태스크 ID

        Returns:
            취소 성공 여부
        """
        try:
            task_result = AsyncResult(task_id)
            task_result.revoke(terminate=True, signal='SIGKILL')
            logger.info(f"분석 태스크 취소 요청: task_id={task_id}")
            return True
        except Exception as e:
            logger.error(f"태스크 취소 실패: task_id={task_id}, error={e}")
            return False
