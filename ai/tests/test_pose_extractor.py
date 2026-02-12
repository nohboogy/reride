"""포즈 추출기 기본 테스트 (영상 파일 없이 단위 테스트)."""

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai.pose_estimation.extractor import PoseFrame, PoseExtractor, poses_to_numpy


def test_calculate_angle():
    """세 점의 각도 계산 테스트."""
    # 직각 (90도)
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 0.0, 0.0])
    c = np.array([0.0, 1.0, 0.0])
    angle = PoseExtractor._calculate_angle(a, b, c)
    assert abs(angle - 90.0) < 0.1, f"Expected ~90, got {angle}"

    # 일직선 (180도)
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 0.0, 0.0])
    c = np.array([-1.0, 0.0, 0.0])
    angle = PoseExtractor._calculate_angle(a, b, c)
    assert abs(angle - 180.0) < 0.1, f"Expected ~180, got {angle}"

    print("test_calculate_angle PASSED")


def test_poses_to_numpy():
    """PoseFrame → numpy 변환 테스트."""
    # 더미 PoseFrame 생성
    landmarks = np.random.rand(33, 4).astype(np.float32)
    pf = PoseFrame(
        frame_idx=0,
        timestamp_ms=0.0,
        landmarks=landmarks,
        center_of_mass=np.array([0.5, 0.5, 0.0]),
        board_angle=10.0,
        knee_angle_left=140.0,
        knee_angle_right=145.0,
        is_airborne=False,
    )

    result = poses_to_numpy([pf, pf])
    assert result.shape == (2, 138), f"Expected (2, 138), got {result.shape}"
    print("test_poses_to_numpy PASSED")


def test_pose_frame_creation():
    """PoseFrame 데이터 구조 테스트."""
    landmarks = np.zeros((33, 4), dtype=np.float32)
    pf = PoseFrame(
        frame_idx=42,
        timestamp_ms=2800.0,
        landmarks=landmarks,
        center_of_mass=np.array([0.5, 0.6, 0.0]),
        board_angle=-5.3,
        knee_angle_left=150.0,
        knee_angle_right=148.0,
        is_airborne=True,
    )

    assert pf.frame_idx == 42
    assert pf.is_airborne is True
    assert pf.landmarks.shape == (33, 4)
    print("test_pose_frame_creation PASSED")


if __name__ == "__main__":
    test_calculate_angle()
    test_poses_to_numpy()
    test_pose_frame_creation()
    print("\nAll tests passed!")
