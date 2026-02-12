"""포즈 추출 결과를 영상 위에 시각화하는 모듈."""

import cv2
import numpy as np

from ai.pose_estimation.extractor import PoseFrame


# MediaPipe pose landmark indices (compatible with MediaPipe 0.10+)
# 스노우보드 분석에 중요한 관절 연결
SNOWBOARD_CONNECTIONS = [
    (11, 12),  # LEFT_SHOULDER - RIGHT_SHOULDER
    (23, 24),  # LEFT_HIP - RIGHT_HIP
    (11, 23),  # LEFT_SHOULDER - LEFT_HIP
    (12, 24),  # RIGHT_SHOULDER - RIGHT_HIP
    (23, 25),  # LEFT_HIP - LEFT_KNEE
    (24, 26),  # RIGHT_HIP - RIGHT_KNEE
    (25, 27),  # LEFT_KNEE - LEFT_ANKLE
    (26, 28),  # RIGHT_KNEE - RIGHT_ANKLE
    (27, 31),  # LEFT_ANKLE - LEFT_FOOT_INDEX
    (28, 32),  # RIGHT_ANKLE - RIGHT_FOOT_INDEX
    # Add arm connections for better visualization
    (11, 13),  # LEFT_SHOULDER - LEFT_ELBOW
    (13, 15),  # LEFT_ELBOW - LEFT_WRIST
    (12, 14),  # RIGHT_SHOULDER - RIGHT_ELBOW
    (14, 16),  # RIGHT_ELBOW - RIGHT_WRIST
]


def draw_pose_on_frame(frame: np.ndarray, pose_frame: PoseFrame) -> np.ndarray:
    """프레임에 포즈 오버레이를 그린다."""
    h, w = frame.shape[:2]
    overlay = frame.copy()

    landmarks = pose_frame.landmarks

    # 관절 점 그리기
    for i, (x, y, z, vis) in enumerate(landmarks):
        if vis > 0.5:
            px, py = int(x * w), int(y * h)
            color = (0, 255, 0) if not pose_frame.is_airborne else (0, 165, 255)
            cv2.circle(overlay, (px, py), 4, color, -1)

    # 연결선 그리기
    for s_idx, e_idx in SNOWBOARD_CONNECTIONS:
        if landmarks[s_idx, 3] > 0.5 and landmarks[e_idx, 3] > 0.5:
            sx, sy = int(landmarks[s_idx, 0] * w), int(landmarks[s_idx, 1] * h)
            ex, ey = int(landmarks[e_idx, 0] * w), int(landmarks[e_idx, 1] * h)
            color = (0, 255, 0) if not pose_frame.is_airborne else (0, 165, 255)
            cv2.line(overlay, (sx, sy), (ex, ey), color, 2)

    # 정보 표시
    info_y = 30
    cv2.putText(overlay, f"Board Angle: {pose_frame.board_angle:.1f}°", (10, info_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    info_y += 25
    cv2.putText(overlay, f"Knee L: {pose_frame.knee_angle_left:.0f}° R: {pose_frame.knee_angle_right:.0f}°",
                (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    info_y += 25
    if pose_frame.is_airborne:
        cv2.putText(overlay, "AIRBORNE!", (10, info_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)

    return overlay


def create_pose_video(
    video_path: str,
    pose_frames: list[PoseFrame],
    output_path: str,
    sample_fps: int = 15,
) -> str:
    """포즈 오버레이가 있는 영상을 생성한다. 원본 프레임레이트 유지."""
    cap = cv2.VideoCapture(video_path)
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_interval = max(1, int(original_fps / sample_fps))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    # Use ORIGINAL fps, not sample_fps
    out = cv2.VideoWriter(output_path, fourcc, original_fps, (width, height))

    # Build a mapping from frame_idx to pose_frame for quick lookup
    pose_map = {pf.frame_idx: pf for pf in pose_frames}

    frame_idx = 0
    current_pose = None  # Most recent pose to use for in-between frames

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Check if we have a pose for this exact frame
        if frame_idx in pose_map:
            current_pose = pose_map[frame_idx]

        # Draw pose overlay if we have pose data
        if current_pose is not None:
            frame = draw_pose_on_frame(frame, current_pose)

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    return output_path
