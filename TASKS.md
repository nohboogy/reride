# reride - 작업 현황

마지막 업데이트: 2026-02-16

## 현재 상태 요약

### Frontend (Flutter)
- ✅ 앱 구조, 테마, 라우터 세팅
- ✅ HomeScreen (영상 목록 + pull-to-refresh + 삭제 → Phase 2 서브에이전트 작업 중)
- ✅ UploadScreen (영상 업로드)
- ✅ AnalysisResultScreen (분석 결과)
- ✅ ApiService (HTTP 클라이언트, deleteAnalysis 추가)
- ✅ ProfileScreen (서브에이전트 작업 중)
- ✅ LoginScreen / RegisterScreen
- ✅ AuthProvider (토큰 저장/로드)
- ✅ Router guard (미로그인 → /login)

### Backend (FastAPI)
- ✅ FastAPI 앱 구조
- ✅ POST/GET /api/v1/analyses
- ✅ GET/DELETE /api/v1/analyses/{id}
- ✅ POST /api/v1/auth/register, /login, /logout
- ✅ GET/PATCH /api/v1/auth/me
- ✅ SQLite 로컬 DB
- ✅ AI pipeline 구조

## 작업 우선순위

### Phase 1: 버그 수정 + Auth ✅ 완료 (2026-02-16)
1. [x] `api_service.dart` - `getVideos()` → `listAnalyses()` 수정
2. [x] 로그인 화면 (`login_screen.dart`)
3. [x] 회원가입 화면 (`register_screen.dart`)
4. [x] Auth Provider (토큰 저장/로드, flutter_secure_storage 사용)
5. [x] 라우터에 로그인 가드 추가

### Phase 2: UI 완성 (서브에이전트 진행 중)
6. [ ] ProfileScreen 완성
7. [ ] 홈화면 pull-to-refresh + 실제 API 연결
8. [ ] 영상 삭제 기능 (swipe-to-delete / long press)

### Phase 3: 백엔드-프론트 연동 완성 ✅ 완료 (2026-02-16)
9. [x] API 엔드포인트 불일치 수정 (getProfile 경로, deleteAnalysis 추가)
10. [x] 백엔드 누락 엔드포인트 추가 (PATCH /auth/me, DELETE /analyses/{id}, POST /auth/logout)

### Phase 4: 다음 할 일
- [ ] 백엔드 실제 실행 테스트 (uvicorn 로컬 실행)
- [ ] Flutter 앱 실제 실행 테스트 (flutter run)
- [ ] 영상 업로드 → AI 분석 → 결과 표시 E2E 플로우 검증
- [ ] AI 파이프라인 연동 확인 (mediapipe, pytorch 실제 동작)

## 파일 구조
- workspace: /Users/wooseokro/.openclaw/workspace/reride
- frontend: /Users/wooseokro/.openclaw/workspace/reride/frontend
- backend: /Users/wooseokro/.openclaw/workspace/reride/backend
