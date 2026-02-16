# reride - 작업 현황

마지막 업데이트: 2026-02-16

## 현재 상태 요약

### Frontend (Flutter)
- ✅ 앱 구조, 테마, 라우터 세팅
- ✅ HomeScreen (영상 목록 + pull-to-refresh + 삭제)
- ✅ UploadScreen (영상 업로드)
- ✅ AnalysisResultScreen (분석 결과 + 폴링)
- ✅ ApiService (HTTP 클라이언트)
- ✅ ProfileScreen (API 연결, 통계, 로그아웃)
- ✅ LoginScreen / RegisterScreen
- ✅ AuthProvider (flutter_secure_storage)
- ✅ Router guard
- ✅ 웹 빌드 성공 (flutter build web)

### Backend (FastAPI, Python 3.11)
- ✅ FastAPI 앱 (uvicorn, SQLite, aiosqlite)
- ✅ POST/GET/DELETE /api/v1/analyses
- ✅ POST /api/v1/auth/register, /login, /logout
- ✅ GET/PATCH /api/v1/auth/me
- ✅ 파일 업로드 → DB 저장 → processing 상태 전환 E2E 확인
- ✅ Python 3.11 venv 세팅 완료
- ⏳ AI 파이프라인 (numpy/mediapipe/torch) 설치 중 (서브에이전트)

### AI Pipeline
- ✅ 코드 구조: pose_estimation, trick_classification, character_animation
- ✅ mediapipe pose landmarker 모델 파일 존재
- ⏳ numpy, opencv, mediapipe, torch 설치 중

## 완료된 Phase

### Phase 1: Auth ✅
### Phase 2: UI 완성 ✅
### Phase 3: API 연동 수정 ✅
### Phase 4: 백엔드 실행 + 업로드 E2E ✅

## 다음 할 일 (Phase 5)

- [ ] AI 파이프라인 임포트 성공 확인 (서브에이전트 완료 후)
- [ ] 실제 스노보드 영상으로 분석 파이프라인 실행 테스트
- [ ] 분석 결과가 Flutter 앱에 표시되는 전체 E2E 확인
- [ ] `.env` 파일 정비 (SECRET_KEY 등 실제 값 설정)
- [ ] Flutter 앱 Android/iOS 빌드 테스트

## 실행 방법

### 백엔드
```bash
cd reride/backend
source .venv/bin/activate  # Python 3.11
uvicorn app.main:app --reload --port 8000
```

### 프론트엔드
```bash
cd reride/frontend
flutter run -d chrome      # 웹
flutter run -d macos       # macOS 데스크탑
```

## 파일 구조
- workspace: /Users/wooseokro/.openclaw/workspace/reride
- frontend: reride/frontend
- backend: reride/backend (venv: backend/.venv)
- AI: reride/ai
