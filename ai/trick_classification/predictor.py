"""트릭 분류 추론 모듈."""

import numpy as np
import torch
from dataclasses import dataclass
from pathlib import Path

from ai.trick_classification.model import TrickClassifier, TrickSegmenter, TRICK_CLASSES
from ai.pose_estimation.extractor import PoseFrame, poses_to_numpy


@dataclass
class TrickPrediction:
    """트릭 탐지 결과."""
    trick_type: str
    confidence: float
    start_frame: int
    end_frame: int
    start_time_ms: float
    end_time_ms: float


@dataclass
class AnalysisScores:
    """자세 분석 점수."""
    overall_score: float          # 0-100 종합 점수
    difficulty_score: float       # 0-100 난이도 점수
    stability_score: float        # 0-100 안정성 점수
    feedback: list[str]           # 피드백 메시지 리스트


class TrickPredictor:
    """트릭 분류 및 자세 분석 추론기."""

    def __init__(self, model_path: str | None = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = TrickClassifier().to(self.device)
        self.model.eval()

        if model_path and Path(model_path).exists():
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)

    def detect_tricks(self, pose_frames: list[PoseFrame]) -> list[TrickPrediction]:
        """포즈 데이터에서 트릭을 탐지한다.

        현재는 규칙 기반 + 간단한 휴리스틱으로 동작하며,
        학습 데이터가 충분해지면 ML 모델로 전환한다.
        """
        if not pose_frames:
            return []

        tricks = []

        # 공중 구간 탐지 (점프 계열 트릭)
        airborne_segments = self._find_airborne_segments(pose_frames)
        for start_idx, end_idx in airborne_segments:
            segment = pose_frames[start_idx:end_idx + 1]
            trick = self._classify_airborne_trick(segment, start_idx, end_idx)
            if trick:
                tricks.append(trick)

        # 비공중 트릭 탐지 (버터링, 카빙 등)
        ground_tricks = self._detect_ground_tricks(pose_frames)
        tricks.extend(ground_tricks)

        # 시간 순 정렬
        tricks.sort(key=lambda t: t.start_frame)
        return tricks

    def analyze_posture(self, pose_frames: list[PoseFrame]) -> AnalysisScores:
        """자세 분석 및 점수 산정."""
        if not pose_frames:
            return AnalysisScores(0, 0, 0, ["포즈를 감지할 수 없습니다"])

        feedback = []

        # 안정성 점수: 무게중심 변동성
        com_y = [pf.center_of_mass[1] for pf in pose_frames]
        com_variation = np.std(com_y)
        stability = max(0, min(100, 100 - com_variation * 500))

        # 무릎 굽힘 분석
        avg_knee_left = np.mean([pf.knee_angle_left for pf in pose_frames])
        avg_knee_right = np.mean([pf.knee_angle_right for pf in pose_frames])
        avg_knee = (avg_knee_left + avg_knee_right) / 2

        if avg_knee > 170:
            feedback.append("무릎을 더 굽혀 낮은 자세를 유지하면 안정성이 향상됩니다")
            stability *= 0.8
        elif avg_knee < 120:
            feedback.append("무릎이 과도하게 굽혀져 있습니다. 적당히 펴서 균형을 잡으세요")
        else:
            feedback.append("적절한 무릎 굽힘 각도를 유지하고 있습니다")

        # 보드 각도 분석
        board_angles = [abs(pf.board_angle) for pf in pose_frames]
        avg_board_angle = np.mean(board_angles)
        board_variation = np.std(board_angles)

        if board_variation > 15:
            feedback.append("보드 각도 변화가 큽니다. 에지 컨트롤 연습이 필요합니다")

        # 난이도 점수: 트릭 수 + 공중 시간
        airborne_ratio = sum(1 for pf in pose_frames if pf.is_airborne) / len(pose_frames)
        difficulty = min(100, airborne_ratio * 200 + board_variation * 2)

        # 종합 점수
        overall = (stability * 0.4 + difficulty * 0.3 + min(100, avg_knee / 1.8) * 0.3)

        if overall >= 80:
            feedback.insert(0, "전반적으로 우수한 라이딩입니다!")
        elif overall >= 60:
            feedback.insert(0, "좋은 라이딩입니다. 아래 피드백을 참고하여 개선해보세요.")
        else:
            feedback.insert(0, "기본기를 다지는 단계입니다. 꾸준히 연습하세요!")

        return AnalysisScores(
            overall_score=round(overall, 1),
            difficulty_score=round(difficulty, 1),
            stability_score=round(stability, 1),
            feedback=feedback,
        )

    def _find_airborne_segments(self, pose_frames: list[PoseFrame]) -> list[tuple[int, int]]:
        """연속 공중 구간을 찾는다."""
        segments = []
        start = None

        for i, pf in enumerate(pose_frames):
            if pf.is_airborne and start is None:
                start = i
            elif not pf.is_airborne and start is not None:
                if i - start >= 3:  # 최소 3프레임 이상
                    segments.append((start, i - 1))
                start = None

        if start is not None and len(pose_frames) - start >= 3:
            segments.append((start, len(pose_frames) - 1))

        return segments

    def _classify_airborne_trick(
        self, segment: list[PoseFrame], start_idx: int, end_idx: int
    ) -> TrickPrediction | None:
        """공중 구간의 트릭을 분류한다 (규칙 기반)."""
        if not segment:
            return None

        # 회전량 추정 (어깨 방향 변화)
        shoulder_angles = []
        for pf in segment:
            left_s = pf.landmarks[11, :2]  # LEFT_SHOULDER
            right_s = pf.landmarks[12, :2]  # RIGHT_SHOULDER
            angle = np.degrees(np.arctan2(right_s[1] - left_s[1], right_s[0] - left_s[0]))
            shoulder_angles.append(angle)

        total_rotation = abs(shoulder_angles[-1] - shoulder_angles[0]) if len(shoulder_angles) > 1 else 0

        # 그랩 감지 (손이 발 근처에 있는지)
        has_grab = False
        for pf in segment:
            left_hand = pf.landmarks[19, :2]   # LEFT_INDEX
            right_hand = pf.landmarks[20, :2]  # RIGHT_INDEX
            left_foot = pf.landmarks[31, :2]
            right_foot = pf.landmarks[32, :2]
            foot_center = (left_foot + right_foot) / 2

            if np.linalg.norm(left_hand - foot_center) < 0.1 or np.linalg.norm(right_hand - foot_center) < 0.1:
                has_grab = True
                break

        # 분류
        if has_grab:
            trick_type = "grab_indy"
            confidence = 0.6
        elif total_rotation > 150:
            trick_type = "jump_360"
            confidence = 0.5 + min(0.4, total_rotation / 500)
        elif total_rotation > 80:
            trick_type = "jump_180"
            confidence = 0.6 + min(0.3, total_rotation / 300)
        elif len(segment) >= 3:
            trick_type = "jump_straight"
            confidence = 0.7
        else:
            return None

        return TrickPrediction(
            trick_type=trick_type,
            confidence=round(confidence, 2),
            start_frame=segment[0].frame_idx,
            end_frame=segment[-1].frame_idx,
            start_time_ms=segment[0].timestamp_ms,
            end_time_ms=segment[-1].timestamp_ms,
        )

    def _detect_ground_tricks(self, pose_frames: list[PoseFrame]) -> list[TrickPrediction]:
        """비공중 트릭을 탐지한다."""
        tricks = []

        # 카빙 탐지: 보드 각도가 크게 변하는 구간
        window_size = 10
        for i in range(0, len(pose_frames) - window_size, window_size // 2):
            window = pose_frames[i:i + window_size]
            if any(pf.is_airborne for pf in window):
                continue

            angles = [pf.board_angle for pf in window]
            angle_range = max(angles) - min(angles)

            if angle_range > 20:
                tricks.append(TrickPrediction(
                    trick_type="carving",
                    confidence=min(0.9, 0.5 + angle_range / 100),
                    start_frame=window[0].frame_idx,
                    end_frame=window[-1].frame_idx,
                    start_time_ms=window[0].timestamp_ms,
                    end_time_ms=window[-1].timestamp_ms,
                ))

        return tricks
