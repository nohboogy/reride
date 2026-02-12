# Reride - 시스템 아키텍처

## 프로젝트 구조

```
reride/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py            # FastAPI 앱 엔트리포인트
│   │   ├── config.py          # 설정 관리
│   │   ├── api/               # API 라우터
│   │   │   ├── auth.py        # 인증 API
│   │   │   ├── videos.py      # 영상 업로드/조회 API
│   │   │   └── analysis.py    # 분석 결과 API
│   │   ├── core/              # 핵심 유틸리티
│   │   │   ├── database.py    # DB 연결
│   │   │   ├── security.py    # JWT, 해싱
│   │   │   └── storage.py     # S3 파일 저장
│   │   ├── models/            # SQLAlchemy 모델
│   │   │   ├── user.py
│   │   │   ├── video.py
│   │   │   └── analysis.py
│   │   ├── schemas/           # Pydantic 스키마
│   │   │   ├── user.py
│   │   │   ├── video.py
│   │   │   └── analysis.py
│   │   ├── services/          # 비즈니스 로직
│   │   │   ├── video_service.py
│   │   │   └── analysis_service.py
│   │   └── workers/           # Celery 비동기 워커
│   │       └── analyze_video.py
│   ├── requirements.txt
│   └── tests/
├── ai/                        # AI/ML 모듈
│   ├── pose_estimation/       # 포즈 추출
│   │   ├── extractor.py       # MediaPipe 포즈 추출기
│   │   └── visualizer.py      # 포즈 시각화
│   ├── trick_classification/  # 트릭 분류
│   │   ├── model.py           # LSTM 분류 모델
│   │   ├── trainer.py         # 학습 스크립트
│   │   └── predictor.py       # 추론
│   ├── character_animation/   # 캐릭터 애니메이션
│   │   ├── renderer.py        # 2D 캐릭터 렌더러
│   │   ├── mapper.py          # 포즈→캐릭터 매핑
│   │   └── video_builder.py   # 애니메이션 영상 생성
│   └── pipeline.py            # 전체 AI 파이프라인 오케스트레이터
├── frontend/                  # Flutter 앱 (별도 진행)
├── docker-compose.yml         # 로컬 개발 환경
└── .env.example               # 환경 변수 템플릿
```

## 데이터 흐름

```
[사용자] → 영상 업로드 → [FastAPI] → S3 저장
                                    → [Celery Worker] 비동기 분석 시작
                                        → 1. 영상 프레임 추출 (OpenCV)
                                        → 2. 포즈 추출 (MediaPipe)
                                        → 3. 트릭 분류 (LSTM)
                                        → 4. 자세 분석 & 점수 산정
                                        → 5. 캐릭터 애니메이션 렌더링
                                        → 6. 결과 저장 (DB + S3)
                                    → 알림 (분석 완료)
[사용자] ← 분석 결과 조회 ← [FastAPI]
```

## 기술 스택

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Celery
- **AI/ML**: MediaPipe, PyTorch, OpenCV, NumPy
- **DB**: PostgreSQL (데이터) + Redis (캐시/큐) + S3 (파일)
- **Frontend**: Flutter (Dart)
- **Infra**: Docker, AWS (EC2, S3, CloudFront)
