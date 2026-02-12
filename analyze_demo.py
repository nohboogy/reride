"""
Reride 데모 스크립트.

사용법:
    python analyze_demo.py <영상 파일 경로> [--style default|neon|retro]

예시:
    python analyze_demo.py my_snowboard_video.mp4
    python analyze_demo.py my_snowboard_video.mp4 --style neon
"""

import argparse
import logging
import sys
from pathlib import Path

# 프로젝트 루트를 PYTHONPATH에 추가
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "backend"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    parser = argparse.ArgumentParser(description="Reride - 스노우보드 영상 분석")
    parser.add_argument("video", help="분석할 영상 파일 경로", default="D:/보드 영상/231230 우석 용평 트릭.MP4")
    parser.add_argument("--style", choices=["default", "neon", "retro"], default="default",
                        help="캐릭터 스타일 (기본: default)")
    parser.add_argument("--output-dir", default="outputs", help="출력 디렉터리")
    parser.add_argument("--fps", type=int, default=15, help="분석 FPS (기본: 15)")
    parser.add_argument("--no-animation", action="store_true", help="캐릭터 애니메이션 생성 건너뛰기")
    args = parser.parse_args()

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"오류: 영상 파일을 찾을 수 없습니다: {video_path}")
        sys.exit(1)

    from ai.pipeline import ReridePipeline

    video_id = video_path.stem

    print(f"\n{'='*60}")
    print(f"  Reride - 스노우보드 영상 분석")
    print(f"{'='*60}")
    print(f"  영상: {video_path}")
    print(f"  스타일: {args.style}")
    print(f"  출력 폴더: {args.output_dir}")
    print(f"{'='*60}\n")

    with ReridePipeline(output_dir=args.output_dir) as pipeline:
        result = pipeline.analyze(
            video_path=str(video_path),
            video_id=video_id,
            style=args.style,
            sample_fps=args.fps,
            generate_animation=not args.no_animation,
            generate_overlay=True,
        )

    print(f"\n{'='*60}")
    print(f"  분석 결과")
    print(f"{'='*60}")
    print(f"  총 프레임: {result.total_frames}")
    print(f"  공중 프레임: {result.airborne_frames}")
    print(f"")
    print(f"  종합 점수: {result.scores.overall_score}/100")
    print(f"  난이도 점수: {result.scores.difficulty_score}/100")
    print(f"  안정성 점수: {result.scores.stability_score}/100")
    print(f"")

    if result.tricks:
        print(f"  감지된 트릭 ({len(result.tricks)}개):")
        for i, trick in enumerate(result.tricks, 1):
            print(f"    {i}. {trick.trick_type} (신뢰도: {trick.confidence:.0%})")
    else:
        print(f"  감지된 트릭: 없음")

    print(f"")
    print(f"  피드백:")
    for fb in result.scores.feedback:
        print(f"    - {fb}")

    if result.animation_path:
        print(f"\n  캐릭터 애니메이션: {result.animation_path}")
    if result.overlay_path:
        print(f"  포즈 오버레이 영상: {result.overlay_path}")
    if result.highlight_path:
        print(f"  하이라이트 영상: {result.highlight_path}")

    print(f"\n  상세 결과: {args.output_dir}/{video_id}_summary.json")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
