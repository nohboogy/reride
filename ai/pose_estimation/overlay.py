"""
MediaPipe 포즈 오버레이 모듈.

원본 영상에 MediaPipe 포즈 키포인트를 오버레이하여
스켈레톤 애니메이션을 생성한다.
"""

import cv2
import numpy as np
from pathlib import Path
from .extractor import PoseFrame


# MediaPipe Pose 스켈레톤 연결 정의
POSE_CONNECTIONS = [
    # Torso
    (11, 12),  # Left shoulder - Right shoulder
    (11, 23),  # Left shoulder - Left hip
    (12, 24),  # Right shoulder - Right hip
    (23, 24),  # Left hip - Right hip

    # Left arm
    (11, 13),  # Left shoulder - Left elbow
    (13, 15),  # Left elbow - Left wrist

    # Right arm
    (12, 14),  # Right shoulder - Right elbow
    (14, 16),  # Right elbow - Right wrist

    # Left leg
    (23, 25),  # Left hip - Left knee
    (25, 27),  # Left knee - Left ankle
    (27, 29),  # Left ankle - Left heel
    (27, 31),  # Left ankle - Left foot index
    (29, 31),  # Left heel - Left foot index

    # Right leg
    (24, 26),  # Right hip - Right knee
    (26, 28),  # Right knee - Right ankle
    (28, 30),  # Right ankle - Right heel
    (28, 32),  # Right ankle - Right foot index
    (30, 32),  # Right heel - Right foot index
]

# Face connections (optional)
FACE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7),  # Left eye
    (0, 4), (4, 5), (5, 6), (6, 8),  # Right eye
    (9, 10),  # Mouth
]


def build_overlay_video(
    video_path: str,
    pose_frames: list[PoseFrame],
    output_path: str,
    fps: int = 15,
    draw_face: bool = False,
    confidence_threshold: float = 0.5,
    point_color: tuple = (0, 255, 0),  # Green
    line_color: tuple = (255, 255, 255),  # White
    point_radius: int = 5,
    line_thickness: int = 2,
) -> str:
    """
    Overlay pose keypoints on original video.

    Args:
        video_path: Original video path
        pose_frames: List of PoseFrame from extractor
        output_path: Output video path
        fps: Output FPS (should match pose extraction fps)
        draw_face: Whether to draw face landmarks
        confidence_threshold: Min visibility to draw point
        point_color: BGR color for joints
        line_color: BGR color for skeleton lines
        point_radius: Size of joint circles
        line_thickness: Width of skeleton lines

    Returns:
        Output video path
    """
    # Open original video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    # Get video properties
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Create pose frame index mapping
    # pose_frames may be sampled, so map frame_idx to PoseFrame
    pose_dict = {pf.frame_idx: pf for pf in pose_frames}

    # Setup video writer
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        cap.release()
        raise ValueError(f"Cannot create video writer: {output_path}")

    print(f"Creating overlay video: {output_path}")
    print(f"Original FPS: {original_fps:.1f}, Output FPS: {fps}")
    print(f"Resolution: {width}x{height}")
    print(f"Total frames: {total_frames}, Pose frames: {len(pose_frames)}")

    # Determine frame sampling strategy
    frame_interval = max(1, int(original_fps / fps))

    frame_idx = 0
    processed_count = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Only process frames at desired fps
            if frame_idx % frame_interval == 0:
                # Draw pose if available for this frame
                if frame_idx in pose_dict:
                    pose_frame = pose_dict[frame_idx]
                    frame = _draw_pose_on_frame(
                        frame,
                        pose_frame,
                        width,
                        height,
                        draw_face=draw_face,
                        confidence_threshold=confidence_threshold,
                        point_color=point_color,
                        line_color=line_color,
                        point_radius=point_radius,
                        line_thickness=line_thickness,
                    )

                out.write(frame)
                processed_count += 1

                if processed_count % 30 == 0:
                    print(f"Processed {processed_count} frames...")

            frame_idx += 1

    finally:
        cap.release()
        out.release()

    print(f"Overlay complete: {processed_count} frames written to {output_path}")
    return output_path


def _draw_pose_on_frame(
    frame: np.ndarray,
    pose_frame: PoseFrame,
    width: int,
    height: int,
    draw_face: bool,
    confidence_threshold: float,
    point_color: tuple,
    line_color: tuple,
    point_radius: int,
    line_thickness: int,
) -> np.ndarray:
    """Draw pose landmarks and skeleton on a single frame."""
    landmarks = pose_frame.landmarks

    # Convert normalized coordinates to pixel coordinates
    pixel_coords = landmarks[:, :2].copy()
    pixel_coords[:, 0] *= width
    pixel_coords[:, 1] *= height
    pixel_coords = pixel_coords.astype(int)

    # Get visibility scores
    visibility = landmarks[:, 3]

    # Select connections to draw
    connections = POSE_CONNECTIONS.copy()
    if draw_face:
        connections.extend(FACE_CONNECTIONS)

    # Draw skeleton lines first (so points appear on top)
    for start_idx, end_idx in connections:
        if (visibility[start_idx] >= confidence_threshold and
            visibility[end_idx] >= confidence_threshold):
            start_point = tuple(pixel_coords[start_idx])
            end_point = tuple(pixel_coords[end_idx])
            cv2.line(frame, start_point, end_point, line_color, line_thickness)

    # Draw joint points
    for i in range(len(landmarks)):
        if visibility[i] >= confidence_threshold:
            # Skip face landmarks if not requested
            if not draw_face and i < 11:
                continue

            center = tuple(pixel_coords[i])
            cv2.circle(frame, center, point_radius, point_color, -1)

            # Optional: draw a border for better visibility
            cv2.circle(frame, center, point_radius + 1, (0, 0, 0), 1)

    # Optional: draw info overlay
    info_text = f"Frame {pose_frame.frame_idx} | Airborne: {pose_frame.is_airborne}"
    cv2.putText(
        frame,
        info_text,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        frame,
        info_text,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        1,
    )

    return frame


def create_overlay_from_video(
    video_path: str,
    output_path: str | None = None,
    sample_fps: int = 15,
    **overlay_kwargs,
) -> str:
    """
    Convenience function to extract poses and create overlay in one step.

    Args:
        video_path: Input video path
        output_path: Output path (default: video_path with _overlay suffix)
        sample_fps: FPS for pose extraction and overlay
        **overlay_kwargs: Additional arguments for build_overlay_video

    Returns:
        Output video path
    """
    from .extractor import extract_poses

    # Extract poses
    print("Extracting poses...")
    pose_frames = extract_poses(video_path, sample_fps=sample_fps)

    if not pose_frames:
        raise ValueError("No poses detected in video")

    # Determine output path
    if output_path is None:
        video_path_obj = Path(video_path)
        output_path = str(
            video_path_obj.parent / f"{video_path_obj.stem}_overlay{video_path_obj.suffix}"
        )

    # Create overlay
    return build_overlay_video(
        video_path,
        pose_frames,
        output_path,
        fps=sample_fps,
        **overlay_kwargs,
    )
