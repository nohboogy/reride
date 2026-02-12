"""캐릭터 애니메이션 프레임들을 영상으로 조합하는 모듈."""

import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

from ai.pose_estimation.extractor import PoseFrame
from ai.character_animation.renderer import CharacterRenderer


def build_animation_video(
    pose_frames: list[PoseFrame],
    output_path: str,
    fps: int = 15,
    style: str = "default",
    width: int = 720,
    height: int = 720,
) -> str:
    """포즈 데이터를 캐릭터 애니메이션 영상으로 변환한다.

    Args:
        pose_frames: 포즈 프레임 리스트
        output_path: 출력 영상 경로
        fps: 출력 영상 FPS
        style: 캐릭터 스타일 이름
        width: 영상 너비
        height: 영상 높이

    Returns:
        출력 영상 경로
    """
    renderer = CharacterRenderer(width=width, height=height, style=style)

    with tempfile.TemporaryDirectory() as tmpdir:
        frame_paths = []

        for i, pose_frame in enumerate(pose_frames):
            img = renderer.render_frame(pose_frame, frame_number=i)
            frame_path = Path(tmpdir) / f"frame_{i:06d}.png"
            img.save(str(frame_path))
            frame_paths.append(str(frame_path))

        if not frame_paths:
            raise ValueError("렌더링할 프레임이 없습니다")

        # FFmpeg로 영상 생성
        input_pattern = str(Path(tmpdir) / "frame_%06d.png")
        cmd = [
            imageio_ffmpeg.get_ffmpeg_exe(), "-y",
            "-framerate", str(fps),
            "-i", input_pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "23",
            "-preset", "medium",
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg 오류: {result.stderr}")

    return output_path


def build_highlight_video(
    pose_frames: list[PoseFrame],
    tricks: list,
    output_path: str,
    max_duration_seconds: float = 15.0,
    fps: int = 15,
    style: str = "default",
) -> str:
    """트릭 하이라이트만 모아서 15초 쇼트폼 영상을 생성한다.

    Args:
        pose_frames: 전체 포즈 프레임 리스트
        tricks: TrickPrediction 리스트
        output_path: 출력 영상 경로
        max_duration_seconds: 최대 영상 길이
        fps: 출력 FPS
        style: 캐릭터 스타일

    Returns:
        출력 영상 경로
    """
    max_frames = int(max_duration_seconds * fps)

    # 트릭 구간의 프레임만 추출 (전후 여유 프레임 포함)
    highlight_frames = []
    frame_idx_set = set()

    # 프레임 인덱스 → 포즈 프레임 매핑
    idx_to_pose = {pf.frame_idx: pf for pf in pose_frames}

    for trick in sorted(tricks, key=lambda t: -t.confidence):
        padding = 5  # 전후 5프레임 여유
        for fidx in range(trick.start_frame - padding, trick.end_frame + padding + 1):
            if fidx in idx_to_pose and fidx not in frame_idx_set:
                frame_idx_set.add(fidx)
                highlight_frames.append(idx_to_pose[fidx])

        if len(highlight_frames) >= max_frames:
            break

    highlight_frames.sort(key=lambda pf: pf.frame_idx)
    highlight_frames = highlight_frames[:max_frames]

    if not highlight_frames:
        # 트릭이 없으면 전체 영상에서 균등 샘플링
        step = max(1, len(pose_frames) // max_frames)
        highlight_frames = pose_frames[::step][:max_frames]

    return build_animation_video(highlight_frames, output_path, fps, style)
