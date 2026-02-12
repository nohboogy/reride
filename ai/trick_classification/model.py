"""
스노우보드 트릭 분류 LSTM 모델.

포즈 시계열 데이터를 입력받아 트릭 유형을 분류한다.
"""

import torch
import torch.nn as nn


# 지원하는 트릭 유형
TRICK_CLASSES = [
    "straight_ride",   # 직진 주행
    "ollie",           # 올리
    "nollie",          # 놀리
    "jump_straight",   # 직선 점프
    "jump_180",        # 180도 회전 점프
    "jump_360",        # 360도 회전 점프
    "grab_indy",       # 인디 그랩
    "grab_mute",       # 뮤트 그랩
    "rail_50_50",      # 50-50 그라인드
    "rail_boardslide", # 보드슬라이드
    "butter",          # 버터링
    "carving",         # 카빙 턴
]


class TrickClassifier(nn.Module):
    """LSTM 기반 트릭 분류 모델.

    입력: (batch, seq_len, input_dim) 포즈 시계열
    출력: (batch, num_classes) 트릭 클래스 확률
    """

    def __init__(
        self,
        input_dim: int = 138,  # 33*4 + 6 (landmarks + derived features)
        hidden_dim: int = 128,
        num_layers: int = 2,
        num_classes: int = len(TRICK_CLASSES),
        dropout: float = 0.3,
    ):
        super().__init__()

        self.input_norm = nn.LayerNorm(input_dim)

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True,
        )

        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
        )

        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch, seq_len, input_dim) 포즈 시계열

        Returns:
            (batch, num_classes) logits
        """
        x = self.input_norm(x)

        # LSTM
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden*2)

        # Attention pooling
        attn_weights = self.attention(lstm_out)  # (batch, seq_len, 1)
        attn_weights = torch.softmax(attn_weights, dim=1)
        context = torch.sum(lstm_out * attn_weights, dim=1)  # (batch, hidden*2)

        # 분류
        logits = self.classifier(context)
        return logits


class TrickSegmenter(nn.Module):
    """영상 전체에서 트릭 구간을 탐지하는 모델 (프레임별 분류).

    입력: (batch, total_frames, input_dim)
    출력: (batch, total_frames, num_classes + 1)  # +1 for "no_trick" background class
    """

    def __init__(
        self,
        input_dim: int = 138,
        hidden_dim: int = 128,
        num_layers: int = 2,
        num_classes: int = len(TRICK_CLASSES),
        dropout: float = 0.3,
    ):
        super().__init__()

        self.input_norm = nn.LayerNorm(input_dim)

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True,
        )

        self.frame_classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes + 1),  # +1 for background
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.input_norm(x)
        lstm_out, _ = self.lstm(x)
        logits = self.frame_classifier(lstm_out)
        return logits
