"""
MediaPipe 기반 스노우보드 라이딩 포즈 추출기.

영상에서 프레임별로 인체 33개 관절 랜드마크를 추출하고,
스노우보드 분석에 필요한 파생 피처(무게중심, 보드 각도 등)를 계산한다.
"""

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from dataclasses import dataclass
from pathlib import Path
import urllib.request
import os


@dataclass
class PoseFrame:
    """단일 프레임의 포즈 데이터."""
    frame_idx: int
    timestamp_ms: float
    landmarks: np.ndarray  # (33, 4) - x, y, z, visibility
    center_of_mass: np.ndarray  # (3,) - x, y, z
    board_angle: float  # 보드 기울기 (도)
    knee_angle_left: float
    knee_angle_right: float
    is_airborne: bool  # 공중에 떠있는지


class PoseExtractor:
    """MediaPipe를 사용하여 영상에서 포즈를 추출하는 클래스."""

    # MediaPipe 관절 인덱스 매핑
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_FOOT = 31
    RIGHT_FOOT = 32

    def __init__(self, model_complexity: int = 1, min_detection_confidence: float = 0.5):
        # Download model file if not exists
        model_path = self._ensure_model_downloaded()

        # Create PoseLandmarker with new Tasks API
        base_options = python.BaseOptions(model_asset_path=str(model_path))
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5
        )
        self.landmarker = vision.PoseLandmarker.create_from_options(options)
        self._ground_level = None

    def _ensure_model_downloaded(self) -> Path:
        """Download MediaPipe pose model if not exists."""
        # Use lite model for better performance (can switch to heavy if needed)
        model_url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
        model_dir = Path(__file__).parent / "models"
        model_dir.mkdir(exist_ok=True)
        model_path = model_dir / "pose_landmarker_lite.task"

        if not model_path.exists():
            print(f"Downloading MediaPipe pose model to {model_path}...")
            urllib.request.urlretrieve(model_url, model_path)
            print("Download complete.")

        return model_path

    def extract_from_video(self, video_path: str, sample_fps: int = 15) -> list[PoseFrame]:
        """
        영상에서 포즈 데이터를 추출한다.

        Args:
            video_path: 영상 파일 경로
            sample_fps: 초당 추출할 프레임 수 (원본 fps 대비 다운샘플링)

        Returns:
            프레임별 PoseFrame 리스트
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"영상을 열 수 없습니다: {video_path}")

        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = max(1, int(original_fps / sample_fps))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        pose_frames = []
        frame_idx = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                pose_frame = self._process_frame(frame, frame_idx, cap.get(cv2.CAP_PROP_POS_MSEC))
                if pose_frame:
                    pose_frames.append(pose_frame)

            frame_idx += 1

        cap.release()

        # 지면 레벨 추정 및 공중 판정 보정
        if pose_frames:
            self._estimate_ground_and_airborne(pose_frames)

        return pose_frames

    def _process_frame(self, frame: np.ndarray, frame_idx: int, timestamp_ms: float) -> PoseFrame | None:
        """단일 프레임에서 포즈를 추출한다."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Process with new API (timestamp must be in milliseconds as integer)
        results = self.landmarker.detect_for_video(mp_image, int(timestamp_ms))

        if not results.pose_landmarks:
            return None

        # Extract landmarks from first detected pose
        pose_landmarks = results.pose_landmarks[0]

        # Get visibility from world landmarks
        visibility_values = []
        if results.pose_world_landmarks:
            world_landmarks = results.pose_world_landmarks[0]
            visibility_values = [lm.visibility for lm in world_landmarks]
        else:
            visibility_values = [1.0] * 33  # Default visibility

        # Convert to numpy array
        landmarks = np.array([
            [lm.x, lm.y, lm.z, vis]
            for lm, vis in zip(pose_landmarks, visibility_values)
        ])

        # 무게중심 계산 (주요 관절들의 가중 평균)
        key_joints = [self.LEFT_HIP, self.RIGHT_HIP, self.LEFT_SHOULDER, self.RIGHT_SHOULDER]
        com = np.mean(landmarks[key_joints, :3], axis=0)

        # 보드 각도 계산 (양 발의 수평 각도)
        board_angle = self._calculate_board_angle(landmarks)

        # 무릎 각도 계산
        knee_angle_left = self._calculate_angle(
            landmarks[self.LEFT_HIP, :3],
            landmarks[self.LEFT_KNEE, :3],
            landmarks[self.LEFT_ANKLE, :3],
        )
        knee_angle_right = self._calculate_angle(
            landmarks[self.RIGHT_HIP, :3],
            landmarks[self.RIGHT_KNEE, :3],
            landmarks[self.RIGHT_ANKLE, :3],
        )

        return PoseFrame(
            frame_idx=frame_idx,
            timestamp_ms=timestamp_ms,
            landmarks=landmarks,
            center_of_mass=com,
            board_angle=board_angle,
            knee_angle_left=knee_angle_left,
            knee_angle_right=knee_angle_right,
            is_airborne=False,  # 나중에 보정
        )

    def _calculate_board_angle(self, landmarks: np.ndarray) -> float:
        """양 발 사이의 수평 기울기 각도를 계산한다."""
        left_foot = landmarks[self.LEFT_FOOT, :2]
        right_foot = landmarks[self.RIGHT_FOOT, :2]
        diff = right_foot - left_foot
        angle_rad = np.arctan2(diff[1], diff[0])
        return float(np.degrees(angle_rad))

    @staticmethod
    def _calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
        """세 점 사이의 각도를 계산한다 (b가 꼭짓점)."""
        ba = a - b
        bc = c - b
        cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
        cosine = np.clip(cosine, -1.0, 1.0)
        return float(np.degrees(np.arccos(cosine)))

    def _estimate_ground_and_airborne(self, pose_frames: list[PoseFrame]) -> None:
        """
        지면 레벨을 추정하고 공중 상태를 판정한다.
        발의 y좌표 하위 20%를 지면으로 간주하고,
        양 발 모두 지면보다 일정 이상 높으면 공중 상태로 판정.
        """
        foot_y_values = []
        for pf in pose_frames:
            left_y = pf.landmarks[self.LEFT_FOOT, 1]
            right_y = pf.landmarks[self.RIGHT_FOOT, 1]
            foot_y_values.extend([left_y, right_y])

        # MediaPipe의 y좌표는 위가 0, 아래가 1
        ground_level = np.percentile(foot_y_values, 80)
        airborne_threshold = ground_level - 0.05  # 5% 이상 높으면 공중

        for pf in pose_frames:
            left_y = pf.landmarks[self.LEFT_FOOT, 1]
            right_y = pf.landmarks[self.RIGHT_FOOT, 1]
            pf.is_airborne = left_y < airborne_threshold and right_y < airborne_threshold

    def close(self):
        self.landmarker.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def extract_poses(video_path: str, sample_fps: int = 15) -> list[PoseFrame]:
    """포즈 추출 편의 함수."""
    with PoseExtractor() as extractor:
        return extractor.extract_from_video(video_path, sample_fps)


def poses_to_numpy(pose_frames: list[PoseFrame]) -> np.ndarray:
    """PoseFrame 리스트를 모델 입력용 numpy 배열로 변환한다.

    Returns:
        (N, 33*4 + 6) 배열: 33개 관절 x (x,y,z,vis) + com(3) + board_angle + knee_left + knee_right
    """
    rows = []
    for pf in pose_frames:
        flat_landmarks = pf.landmarks.flatten()  # 33*4 = 132
        extra = np.array([
            pf.center_of_mass[0], pf.center_of_mass[1], pf.center_of_mass[2],
            pf.board_angle,
            pf.knee_angle_left,
            pf.knee_angle_right,
        ])
        rows.append(np.concatenate([flat_landmarks, extra]))
    return np.array(rows, dtype=np.float32)
