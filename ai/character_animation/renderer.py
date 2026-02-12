"""
2D 캐릭터 렌더러.

포즈 데이터를 기반으로 귀여운 2D 캐릭터 애니메이션 프레임을 생성한다.
MVP에서는 간단한 벡터 그래픽 기반 캐릭터를 사용한다.
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass

from ai.pose_estimation.extractor import PoseFrame


@dataclass
class CharacterStyle:
    """캐릭터 스타일 설정."""
    name: str = "default"
    body_color: tuple = (70, 130, 220)      # 파란 재킷
    pants_color: tuple = (50, 50, 60)        # 검정 바지
    board_color: tuple = (220, 50, 50)       # 빨강 보드
    helmet_color: tuple = (255, 255, 255)    # 흰 헬멧
    goggle_color: tuple = (255, 165, 0)      # 주황 고글
    skin_color: tuple = (255, 220, 185)      # 피부색
    bg_color: tuple = (200, 230, 255)        # 하늘색 배경
    snow_color: tuple = (240, 245, 255)      # 눈 색
    line_width: int = 3
    head_radius: int = 25
    body_width: int = 20


# 프리셋 스타일
STYLES = {
    "default": CharacterStyle(),
    "neon": CharacterStyle(
        name="neon",
        body_color=(0, 255, 128),
        pants_color=(30, 30, 40),
        board_color=(255, 0, 255),
        helmet_color=(0, 200, 255),
        goggle_color=(255, 255, 0),
        bg_color=(20, 20, 40),
        snow_color=(40, 40, 60),
    ),
    "retro": CharacterStyle(
        name="retro",
        body_color=(200, 100, 50),
        pants_color=(80, 60, 40),
        board_color=(60, 120, 60),
        helmet_color=(220, 200, 170),
        goggle_color=(150, 80, 50),
        bg_color=(180, 210, 230),
        snow_color=(230, 235, 240),
    ),
}


class CharacterRenderer:
    """2D 캐릭터 프레임 렌더러."""

    # MediaPipe 관절 인덱스
    NOSE = 0
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_FOOT = 31
    RIGHT_FOOT = 32

    def __init__(self, width: int = 720, height: int = 720, style: str = "default"):
        self.width = width
        self.height = height
        self.style = STYLES.get(style, STYLES["default"])
        self.margin = 100  # 캐릭터 렌더링 영역 마진

    def render_frame(self, pose_frame: PoseFrame, frame_number: int = 0) -> Image.Image:
        """단일 프레임의 캐릭터를 렌더링한다."""
        img = Image.new("RGB", (self.width, self.height), self.style.bg_color)
        draw = ImageDraw.Draw(img)

        # 배경: 눈 슬로프
        self._draw_background(draw, frame_number)

        # 포즈 좌표를 캔버스 좌표로 변환
        landmarks = pose_frame.landmarks

        def to_canvas(idx):
            x = landmarks[idx, 0]
            y = landmarks[idx, 1]
            cx = int(self.margin + x * (self.width - 2 * self.margin))
            cy = int(self.margin + y * (self.height - 2 * self.margin))
            return (cx, cy)

        # 스노우보드 그리기
        self._draw_board(draw, to_canvas(self.LEFT_FOOT), to_canvas(self.RIGHT_FOOT))

        # 다리 그리기
        self._draw_limb(draw, to_canvas(self.LEFT_HIP), to_canvas(self.LEFT_KNEE), self.style.pants_color, 10)
        self._draw_limb(draw, to_canvas(self.LEFT_KNEE), to_canvas(self.LEFT_ANKLE), self.style.pants_color, 8)
        self._draw_limb(draw, to_canvas(self.RIGHT_HIP), to_canvas(self.RIGHT_KNEE), self.style.pants_color, 10)
        self._draw_limb(draw, to_canvas(self.RIGHT_KNEE), to_canvas(self.RIGHT_ANKLE), self.style.pants_color, 8)

        # 몸통 그리기
        shoulder_mid = self._midpoint(to_canvas(self.LEFT_SHOULDER), to_canvas(self.RIGHT_SHOULDER))
        hip_mid = self._midpoint(to_canvas(self.LEFT_HIP), to_canvas(self.RIGHT_HIP))
        self._draw_body(draw, shoulder_mid, hip_mid)

        # 팔 그리기
        self._draw_limb(draw, to_canvas(self.LEFT_SHOULDER), to_canvas(self.LEFT_ELBOW), self.style.body_color, 8)
        self._draw_limb(draw, to_canvas(self.LEFT_ELBOW), to_canvas(self.LEFT_WRIST), self.style.body_color, 6)
        self._draw_limb(draw, to_canvas(self.RIGHT_SHOULDER), to_canvas(self.RIGHT_ELBOW), self.style.body_color, 8)
        self._draw_limb(draw, to_canvas(self.RIGHT_ELBOW), to_canvas(self.RIGHT_WRIST), self.style.body_color, 6)

        # 장갑 (손)
        self._draw_circle(draw, to_canvas(self.LEFT_WRIST), 8, self.style.pants_color)
        self._draw_circle(draw, to_canvas(self.RIGHT_WRIST), 8, self.style.pants_color)

        # 머리 그리기
        head_pos = to_canvas(self.NOSE)
        self._draw_head(draw, head_pos)

        # 공중이면 이펙트
        if pose_frame.is_airborne:
            self._draw_airborne_effect(draw, hip_mid, frame_number)

        # 눈 파티클
        self._draw_snow_particles(draw, frame_number)

        return img

    def _draw_background(self, draw: ImageDraw.Draw, frame_number: int):
        """눈 슬로프 배경."""
        # 그라데이션 하늘
        for y in range(self.height // 2):
            ratio = y / (self.height // 2)
            r = int(self.style.bg_color[0] * (1 - ratio * 0.3))
            g = int(self.style.bg_color[1] * (1 - ratio * 0.2))
            b = int(self.style.bg_color[2])
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # 눈 슬로프
        slope_y = self.height * 2 // 3
        draw.polygon(
            [(0, slope_y), (self.width, slope_y - 50), (self.width, self.height), (0, self.height)],
            fill=self.style.snow_color,
        )

        # 슬로프 텍스처 라인
        for i in range(5):
            y_offset = slope_y + i * 30 + (frame_number % 20)
            draw.line(
                [(0, y_offset), (self.width, y_offset - 20)],
                fill=tuple(max(0, c - 15) for c in self.style.snow_color),
                width=1,
            )

    def _draw_board(self, draw: ImageDraw.Draw, left_foot: tuple, right_foot: tuple):
        """스노우보드를 그린다."""
        # 보드는 양 발 사이를 잇는 둥근 직사각형
        dx = right_foot[0] - left_foot[0]
        dy = right_foot[1] - left_foot[1]
        length = math.sqrt(dx * dx + dy * dy)
        extend = 20  # 보드가 발 밖으로 나가는 길이

        if length < 1:
            return

        # 방향 벡터
        ux, uy = dx / length, dy / length

        # 보드 끝점 (발보다 좀 더 바깥으로)
        p1 = (left_foot[0] - ux * extend, left_foot[1] - uy * extend)
        p2 = (right_foot[0] + ux * extend, right_foot[1] + uy * extend)

        # 보드 두께
        nx, ny = -uy * 6, ux * 6
        points = [
            (p1[0] + nx, p1[1] + ny),
            (p2[0] + nx, p2[1] + ny),
            (p2[0] - nx, p2[1] - ny),
            (p1[0] - nx, p1[1] - ny),
        ]
        points = [(int(x), int(y)) for x, y in points]
        draw.polygon(points, fill=self.style.board_color)

        # 보드 끝 라운딩
        self._draw_circle(draw, (int(p1[0]), int(p1[1])), 6, self.style.board_color)
        self._draw_circle(draw, (int(p2[0]), int(p2[1])), 6, self.style.board_color)

    def _draw_body(self, draw: ImageDraw.Draw, shoulder: tuple, hip: tuple):
        """재킷(몸통)을 그린다."""
        w = self.style.body_width
        points = [
            (shoulder[0] - w, shoulder[1]),
            (shoulder[0] + w, shoulder[1]),
            (hip[0] + w - 3, hip[1]),
            (hip[0] - w + 3, hip[1]),
        ]
        draw.polygon(points, fill=self.style.body_color)

    def _draw_head(self, draw: ImageDraw.Draw, pos: tuple):
        """헬멧, 고글, 얼굴을 그린다."""
        r = self.style.head_radius

        # 헬멧
        draw.ellipse(
            [pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r],
            fill=self.style.helmet_color,
        )

        # 고글
        goggle_y = pos[1] - 2
        draw.rounded_rectangle(
            [pos[0] - r + 3, goggle_y - 8, pos[0] + r - 3, goggle_y + 8],
            radius=5,
            fill=self.style.goggle_color,
        )

        # 고글 렌즈 반사
        draw.ellipse(
            [pos[0] - 6, goggle_y - 4, pos[0] - 1, goggle_y + 1],
            fill=(255, 255, 255, 180),
        )

        # 입 (작은 미소)
        mouth_y = pos[1] + 10
        draw.arc(
            [pos[0] - 6, mouth_y - 3, pos[0] + 6, mouth_y + 5],
            start=0, end=180,
            fill=(80, 50, 50), width=2,
        )

    def _draw_limb(self, draw: ImageDraw.Draw, start: tuple, end: tuple, color: tuple, width: int):
        """팔/다리를 둥글게 그린다."""
        draw.line([start, end], fill=color, width=width)
        self._draw_circle(draw, start, width // 2, color)
        self._draw_circle(draw, end, width // 2, color)

    def _draw_circle(self, draw: ImageDraw.Draw, center: tuple, radius: int, color: tuple):
        draw.ellipse(
            [center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
            fill=color,
        )

    def _draw_airborne_effect(self, draw: ImageDraw.Draw, center: tuple, frame_number: int):
        """공중 이펙트 (속도선, 파티클)."""
        for i in range(6):
            angle = (frame_number * 30 + i * 60) % 360
            rad = math.radians(angle)
            dist = 40 + (frame_number * 3 + i * 7) % 30
            x = center[0] + int(math.cos(rad) * dist)
            y = center[1] + int(math.sin(rad) * dist)
            length = 15
            ex = x + int(math.cos(rad) * length)
            ey = y + int(math.sin(rad) * length)
            draw.line([(x, y), (ex, ey)], fill=(255, 255, 255, 200), width=2)

    def _draw_snow_particles(self, draw: ImageDraw.Draw, frame_number: int):
        """떨어지는 눈 파티클."""
        np.random.seed(42)
        for i in range(20):
            base_x = np.random.randint(0, self.width)
            base_y = np.random.randint(0, self.height)
            x = (base_x + frame_number * (i % 3 + 1)) % self.width
            y = (base_y + frame_number * 2) % self.height
            size = np.random.randint(2, 5)
            draw.ellipse([x, y, x + size, y + size], fill=(255, 255, 255, 150))

    @staticmethod
    def _midpoint(a: tuple, b: tuple) -> tuple:
        return ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
