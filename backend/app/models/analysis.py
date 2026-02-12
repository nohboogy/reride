from datetime import datetime, timezone

from sqlalchemy import Integer, Float, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"), unique=True, index=True)

    # 트릭 분류 결과
    tricks_detected: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # 예: [{"type": "jump", "confidence": 0.92, "start_frame": 30, "end_frame": 60}]

    # 자세 분석
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    difficulty_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    stability_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # 피드백 (리스트로 저장)
    feedback_text: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # 캐릭터 애니메이션 경로
    animation_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    highlight_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    overlay_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 포즈 데이터 (프레임별 관절 좌표)
    pose_data_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    video = relationship("Video", back_populates="analysis")
