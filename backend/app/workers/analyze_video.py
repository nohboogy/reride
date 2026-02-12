"""영상 분석 Celery 비동기 태스크."""

import logging
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

celery_app = Celery(
    "reride",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # 한 번에 한 태스크만 (GPU 작업이므로)
)

# 동기 DB 엔진 (Celery 워커는 동기로 동작)
sync_engine = create_engine(settings.database_url.replace("+asyncpg", ""))
SyncSession = sessionmaker(bind=sync_engine)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def analyze_video_task(self, video_id: int, style: str = "default"):
    """영상 분석 비동기 태스크.

    1. DB에서 영상 정보 조회
    2. AI 파이프라인 실행
    3. 결과를 DB에 저장
    """
    from app.models.video import Video
    from app.models.analysis import AnalysisResult

    logger.info(f"영상 분석 태스크 시작: video_id={video_id}")

    session = SyncSession()
    try:
        # 영상 상태 업데이트
        video = session.query(Video).filter(Video.id == video_id).first()
        if not video:
            logger.error(f"영상을 찾을 수 없음: {video_id}")
            return {"error": "video_not_found"}

        video.status = "processing"
        session.commit()

        # AI 파이프라인 실행
        from ai.pipeline import ReridePipeline

        with ReridePipeline(output_dir="outputs") as pipeline:
            result = pipeline.analyze(
                video_path=video.storage_path,
                video_id=str(video_id),
                style=style,
            )

        # 결과 저장
        analysis = AnalysisResult(
            video_id=video_id,
            tricks_detected=[
                {
                    "trick_type": t.trick_type,
                    "confidence": t.confidence,
                    "start_frame": t.start_frame,
                    "end_frame": t.end_frame,
                }
                for t in result.tricks
            ],
            overall_score=result.scores.overall_score,
            difficulty_score=result.scores.difficulty_score,
            stability_score=result.scores.stability_score,
            feedback_text=result.scores.feedback,
            animation_path=result.animation_path,
            highlight_path=result.highlight_path,
            overlay_path=result.overlay_path,
            pose_data_path=result.pose_data_path,
        )
        session.add(analysis)
        video.status = "completed"
        session.commit()

        logger.info(f"영상 분석 완료: video_id={video_id}, score={result.scores.overall_score}")
        return {
            "video_id": video_id,
            "overall_score": result.scores.overall_score,
            "tricks_count": len(result.tricks),
        }

    except Exception as e:
        logger.exception(f"영상 분석 실패: video_id={video_id}")
        video = session.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = "failed"
            session.commit()
        raise self.retry(exc=e)

    finally:
        session.close()
