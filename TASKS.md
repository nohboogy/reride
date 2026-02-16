# reride - 작업 현황

마지막 업데이트: 2026-02-16

## 현재 상태 요약

### Frontend (Flutter)
- ✅ 앱 구조, 테마, 라우터 세팅
- ✅ HomeScreen (영상 목록)
- ✅ UploadScreen (영상 업로드)
- ✅ AnalysisResultScreen (분석 결과)
- ✅ ApiService (HTTP 클라이언트)
- ✅ ProfileScreen (기본 구조)
- ❌ 로그인/회원가입 화면 없음
- ❌ `HomeProvider`가 `apiService.getVideos()` 호출하는데 ApiService에 해당 메서드 없음 → `listAnalyses()` 사용해야 함
- ❌ Auth 상태관리 없음 (토큰 저장/로드 로직 미구현)

### Backend (FastAPI)
- ✅ FastAPI 앱 구조
- ✅ analyses, auth, videos API
- ✅ SQLite 로컬 DB
- ✅ AI pipeline 구조

## 작업 우선순위

### Phase 1: 버그 수정 + Auth (현재 진행 중)
1. [ ] `api_service.dart` - `getVideos()` → `listAnalyses()` 수정
2. [ ] 로그인 화면 (`login_screen.dart`)
3. [ ] 회원가입 화면 (`register_screen.dart`)
4. [ ] Auth Provider (토큰 저장/로드, flutter_secure_storage 사용)
5. [ ] 라우터에 로그인 가드 추가

### Phase 2: UI 완성
6. [ ] ProfileScreen 완성
7. [ ] 홈화면 pull-to-refresh
8. [ ] 영상 삭제 기능

### Phase 3: 백엔드 연동 테스트
9. [ ] 백엔드 실행 확인
10. [ ] API 엔드포인트 실제 연동 테스트

## 다음 자동 재개 시 할 일
Phase 1부터 순서대로. TASKS.md의 체크박스 보고 이어서 작업.
workspace: /Users/wooseokro/.openclaw/workspace/reride
frontend: /Users/wooseokro/.openclaw/workspace/reride/frontend
