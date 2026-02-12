"""
전체 AI 분석 파이프라인 오케스트레이터.

영상 입력 → 포즈 추출 → 트릭 분류 → 자세 분석 → 캐릭터 애니메이션 생성
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict

import numpy as np

from ai.pose_estimation.extractor import PoseExtractor, poses_to_numpy
from ai.pose_estimation.overlay import build_overlay_video
from ai.trick_classification.predictor import TrickPredictor, TrickPrediction, AnalysisScores
from ai.character_animation.video_builder import build_animation_video, build_highlight_video

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """파이프라인 실행 결과."""
    tricks: list[TrickPrediction]
    scores: AnalysisScores
    animation_path: str | None
    highlight_path: str | None
    pose_data_path: str | None
    overlay_path: str | None
    total_frames: int
    airborne_frames: int
    pose_frames: list  # List of PoseFrame objects for overlay generation


class ReridePipeline:
    """영상 분석 전체 파이프라인."""

    def __init__(
        self,
        trick_model_path: str | None = None,
        output_dir: str = "outputs",
    ):
        self.pose_extractor = PoseExtractor(model_complexity=1)
        self.trick_predictor = TrickPredictor(model_path=trick_model_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze(
        self,
        video_path: str,
        video_id: str = "unknown",
        style: str = "default",
        sample_fps: int = 15,
        generate_animation: bool = True,
        generate_highlight: bool = True,
        generate_overlay: bool = True,
    ) -> PipelineResult:
        """
        영상을 분석하고 결과를 생성한다.

        Args:
            video_path: 입력 영상 경로
            video_id: 영상 식별자 (출력 파일명에 사용)
            style: 캐릭터 스타일
            sample_fps: 분석 FPS
            generate_animation: 캐릭터 애니메이션 생성 여부
            generate_highlight: 하이라이트 영상 생성 여부
            generate_overlay: 포즈 오버레이 영상 생성 여부

        Returns:
            PipelineResult
        """
        logger.info(f"분석 시작: {video_path} (ID: {video_id})")

        # 1. 포즈 추출
        logger.info("1/5 포즈 추출 중...")
        pose_frames = self.pose_extractor.extract_from_video(video_path, sample_fps)
        logger.info(f"  → {len(pose_frames)}개 프레임에서 포즈 추출 완료")

        if not pose_frames:
            logger.warning("포즈를 감지할 수 없습니다")
            return PipelineResult(
                tricks=[],
                scores=AnalysisScores(0, 0, 0, ["영상에서 사람을 감지할 수 없습니다"]),
                animation_path=None,
                highlight_path=None,
                pose_data_path=None,
                overlay_path=None,
                total_frames=0,
                airborne_frames=0,
                pose_frames=[],
            )

        # Generate overlay video
        overlay_path = None
        if generate_overlay:
            logger.info("Generating pose overlay video...")
            overlay_path = str(self.output_dir / f"{video_id}_overlay.mp4")
            try:
                build_overlay_video(video_path, pose_frames, overlay_path, fps=sample_fps)
                logger.info(f"  → Overlay generated: {overlay_path}")
            except Exception as e:
                logger.error(f"Overlay generation failed: {e}")
                overlay_path = None

        # 2. 트릭 분류
        logger.info("2/5 트릭 분류 중...")
        tricks = self.trick_predictor.detect_tricks(pose_frames)
        logger.info(f"  → {len(tricks)}개 트릭 탐지")

        # 3. 자세 분석
        logger.info("3/5 자세 분석 중...")
        scores = self.trick_predictor.analyze_posture(pose_frames)
        logger.info(f"  → 종합 점수: {scores.overall_score}")

        # 4. 포즈 데이터 저장
        logger.info("4/5 포즈 데이터 저장 중...")
        pose_data_path = str(self.output_dir / f"{video_id}_poses.npy")
        pose_array = poses_to_numpy(pose_frames)
        np.save(pose_data_path, pose_array)

        # 5. 캐릭터 애니메이션 생성
        animation_path = None
        highlight_path = None

        if generate_animation:
            logger.info("5a/5 캐릭터 애니메이션 생성 중...")
            animation_path = str(self.output_dir / f"{video_id}_animation.mp4")
            try:
                build_animation_video(pose_frames, animation_path, fps=sample_fps, style=style)
                logger.info(f"  → 애니메이션 생성 완료: {animation_path}")
            except Exception as e:
                logger.error(f"애니메이션 생성 실패: {e}")
                animation_path = None

        if generate_highlight and tricks:
            logger.info("5b/5 하이라이트 영상 생성 중...")
            highlight_path = str(self.output_dir / f"{video_id}_highlight.mp4")
            try:
                build_highlight_video(pose_frames, tricks, highlight_path, fps=sample_fps, style=style)
                logger.info(f"  → 하이라이트 생성 완료: {highlight_path}")
            except Exception as e:
                logger.error(f"하이라이트 생성 실패: {e}")
                highlight_path = None

        airborne_count = sum(1 for pf in pose_frames if pf.is_airborne)

        result = PipelineResult(
            tricks=tricks,
            scores=scores,
            animation_path=animation_path,
            highlight_path=highlight_path,
            pose_data_path=pose_data_path,
            overlay_path=overlay_path,
            total_frames=len(pose_frames),
            airborne_frames=airborne_count,
            pose_frames=pose_frames,
        )

        # 결과 요약 JSON 저장
        summary_path = self.output_dir / f"{video_id}_summary.json"
        summary = {
            "video_id": video_id,
            "total_frames": result.total_frames,
            "airborne_frames": result.airborne_frames,
            "tricks": [asdict(t) for t in tricks],
            "scores": asdict(scores),
            "animation_path": animation_path,
            "highlight_path": highlight_path,
            "overlay_path": overlay_path,
        }
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

        logger.info(f"분석 완료: {video_id}")
        return result

    def close(self):
        self.pose_extractor.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
