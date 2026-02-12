# Reride Mobile App - Detailed Implementation Plan

**Generated**: 2026-02-05
**Status**: Ready for Implementation
**Estimated Total Effort**: 4-6 weeks (1 developer)

---

## Table of Contents

1. [Phase 1: Backend Services Layer](#phase-1-backend-services-layer)
2. [Phase 2: Flutter App Setup](#phase-2-flutter-app-setup)
3. [Phase 3: Flutter Screens](#phase-3-flutter-screens)
4. [Phase 4: Integration & Testing](#phase-4-integration--testing)
5. [Task Dependency Graph](#task-dependency-graph)

---

## Phase 1: Backend Services Layer

**Goal**: Complete missing business logic layer between API routes and database/AI pipeline.

### 1.1 Create Services Directory Structure

**File**: `D:\Dev_Projects\Reride\backend\app\services\__init__.py`

```
backend/app/services/
├── __init__.py
├── auth_service.py
├── video_service.py
├── analysis_service.py
├── storage_service.py
└── notification_service.py
```

**Dependencies**: None
**Effort**: 5 minutes

---

### 1.2 Auth Service

**File**: `D:\Dev_Projects\Reride\backend\app\services\auth_service.py`

**Functions to implement**:

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `register_user()` | `db: AsyncSession, email: str, username: str, password: str` | `User` | Create new user with hashed password |
| `authenticate_user()` | `db: AsyncSession, email: str, password: str` | `User \| None` | Verify credentials, return user |
| `get_user_by_id()` | `db: AsyncSession, user_id: int` | `User \| None` | Fetch user by ID |
| `get_user_by_email()` | `db: AsyncSession, email: str` | `User \| None` | Fetch user by email |
| `register_social_user()` | `db: AsyncSession, provider: str, provider_id: str, email: str, username: str` | `User` | OAuth user registration |
| `link_social_account()` | `db: AsyncSession, user_id: int, provider: str, provider_id: str` | `bool` | Link OAuth to existing account |

**Dependencies**:
- `D:\Dev_Projects\Reride\backend\app\models\user.py`
- `D:\Dev_Projects\Reride\backend\app\core\security.py`

**Database changes needed**:
- Add `social_accounts` table (new model) for OAuth providers

**Effort**: 2 hours

---

### 1.3 Video Service

**File**: `D:\Dev_Projects\Reride\backend\app\services\video_service.py`

**Functions to implement**:

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `upload_video()` | `db: AsyncSession, user_id: int, file_content: bytes, filename: str, content_type: str` | `Video` | Validate, save to storage, create DB record |
| `get_video()` | `db: AsyncSession, video_id: int, user_id: int` | `Video \| None` | Fetch single video with ownership check |
| `list_videos()` | `db: AsyncSession, user_id: int, skip: int, limit: int` | `tuple[list[Video], int]` | Paginated video list with total count |
| `delete_video()` | `db: AsyncSession, video_id: int, user_id: int` | `bool` | Delete video and associated files |
| `get_video_url()` | `video: Video` | `str` | Generate presigned URL for video access |
| `validate_video_file()` | `content: bytes, content_type: str, max_size_mb: int` | `tuple[bool, str]` | Validate file type and size |

**Dependencies**:
- `D:\Dev_Projects\Reride\backend\app\models\video.py`
- `D:\Dev_Projects\Reride\backend\app\core\storage.py`
- `D:\Dev_Projects\Reride\backend\app\config.py`

**Effort**: 2 hours

---

### 1.4 Analysis Service

**File**: `D:\Dev_Projects\Reride\backend\app\services\analysis_service.py`

**Functions to implement**:

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `request_analysis()` | `db: AsyncSession, video_id: int, user_id: int, style: str` | `dict` | Trigger Celery task, return task_id |
| `get_analysis_status()` | `db: AsyncSession, video_id: int, user_id: int` | `dict` | Return status and progress (0-100%) |
| `get_analysis_result()` | `db: AsyncSession, video_id: int, user_id: int` | `AnalysisResult \| None` | Fetch completed analysis |
| `get_animation_url()` | `analysis: AnalysisResult` | `str \| None` | Presigned URL for animation video |
| `get_highlight_url()` | `analysis: AnalysisResult` | `str \| None` | Presigned URL for highlight video |
| `cancel_analysis()` | `task_id: str` | `bool` | Cancel running Celery task |

**Dependencies**:
- `D:\Dev_Projects\Reride\backend\app\models\analysis.py`
- `D:\Dev_Projects\Reride\backend\app\models\video.py`
- `D:\Dev_Projects\Reride\backend\app\workers\analyze_video.py`
- `D:\Dev_Projects\Reride\backend\app\core\storage.py`

**Celery integration**:
```python
from app.workers.analyze_video import analyze_video_task, celery_app

def request_analysis(db, video_id, user_id, style="default"):
    # Verify ownership
    # Update video status to "queued"
    task = analyze_video_task.delay(video_id, style)
    return {"task_id": task.id, "status": "queued"}

def get_analysis_status(db, video_id, user_id):
    # Check Celery task status via task_id
    # Return progress percentage from task meta
```

**Effort**: 3 hours

---

### 1.5 Notification Service

**File**: `D:\Dev_Projects\Reride\backend\app\services\notification_service.py`

**Functions to implement**:

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `send_push_notification()` | `user_id: int, title: str, body: str, data: dict` | `bool` | Send FCM push to user devices |
| `register_device_token()` | `db: AsyncSession, user_id: int, token: str, platform: str` | `DeviceToken` | Save FCM token |
| `unregister_device_token()` | `db: AsyncSession, token: str` | `bool` | Remove FCM token |
| `notify_analysis_complete()` | `user_id: int, video_id: int, score: float` | `bool` | Send analysis completion notification |

**Database changes needed**:
- Add `device_tokens` table (new model)

**External dependency**: Firebase Admin SDK
- Add to requirements.txt: `firebase-admin==6.5.0`

**Effort**: 2 hours

---

### 1.6 Update API Routes to Use Services

**Files to modify**:

#### `D:\Dev_Projects\Reride\backend\app\api\auth.py`

Changes:
- Import `auth_service`
- Replace direct DB queries with service calls
- Add social login endpoints:
  - `POST /auth/kakao` - Kakao OAuth callback
  - `POST /auth/google` - Google OAuth callback

#### `D:\Dev_Projects\Reride\backend\app\api\videos.py`

Changes:
- Import `video_service`
- Replace direct DB queries with service calls
- Add missing endpoint:
  - `DELETE /{video_id}` - Delete video

#### `D:\Dev_Projects\Reride\backend\app\api\analysis.py`

Changes:
- Import `analysis_service`
- Replace direct DB queries with service calls
- Add missing endpoints:
  - `POST /video/{video_id}/start` - Trigger analysis
  - `GET /video/{video_id}/status` - Get progress (0-100%)

**Effort**: 2 hours

---

### 1.7 New Database Models

**File**: `D:\Dev_Projects\Reride\backend\app\models\social_account.py`

```python
class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider: Mapped[str]  # "kakao", "google"
    provider_user_id: Mapped[str]
    created_at: Mapped[datetime]
```

**File**: `D:\Dev_Projects\Reride\backend\app\models\device_token.py`

```python
class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(unique=True)
    platform: Mapped[str]  # "ios", "android"
    created_at: Mapped[datetime]
```

**Effort**: 1 hour

---

### 1.8 New Pydantic Schemas

**File**: `D:\Dev_Projects\Reride\backend\app\schemas\auth.py` (extend existing)

```python
class SocialLoginRequest(BaseModel):
    provider: str  # "kakao" | "google"
    access_token: str

class AnalysisStartRequest(BaseModel):
    style: str = "default"

class AnalysisStatusResponse(BaseModel):
    video_id: int
    status: str  # "queued" | "processing" | "completed" | "failed"
    progress: int  # 0-100
    task_id: str | None
```

**Effort**: 30 minutes

---

### Phase 1 Summary

| Task | File | Effort | Dependencies |
|------|------|--------|--------------|
| 1.1 Services directory | `services/__init__.py` | 5m | None |
| 1.2 Auth service | `services/auth_service.py` | 2h | 1.1, 1.7 |
| 1.3 Video service | `services/video_service.py` | 2h | 1.1 |
| 1.4 Analysis service | `services/analysis_service.py` | 3h | 1.1, 1.3 |
| 1.5 Notification service | `services/notification_service.py` | 2h | 1.1, 1.7 |
| 1.6 Update API routes | `api/*.py` | 2h | 1.2, 1.3, 1.4 |
| 1.7 New DB models | `models/*.py` | 1h | None |
| 1.8 New schemas | `schemas/*.py` | 30m | None |

**Total Phase 1**: ~13 hours

---

## Phase 2: Flutter App Setup

**Goal**: Initialize Flutter project with proper architecture, dependencies, and core infrastructure.

### 2.1 Create Flutter Project

**Location**: `D:\Dev_Projects\Reride\frontend\`

```bash
flutter create --org com.reride --project-name reride frontend
cd frontend
```

**Effort**: 10 minutes

---

### 2.2 Project Structure

```
D:\Dev_Projects\Reride\frontend\
├── lib/
│   ├── main.dart                    # App entry point
│   ├── app/
│   │   ├── app.dart                 # MaterialApp configuration
│   │   ├── routes.dart              # GoRouter route definitions
│   │   └── theme.dart               # App theme (colors, typography)
│   │
│   ├── core/
│   │   ├── api/
│   │   │   ├── api_client.dart      # Dio configuration
│   │   │   ├── api_endpoints.dart   # API endpoint constants
│   │   │   ├── api_exceptions.dart  # Custom exceptions
│   │   │   └── interceptors/
│   │   │       ├── auth_interceptor.dart
│   │   │       └── error_interceptor.dart
│   │   │
│   │   ├── storage/
│   │   │   ├── secure_storage.dart  # Token storage
│   │   │   └── local_storage.dart   # Hive for cached data
│   │   │
│   │   └── utils/
│   │       ├── constants.dart
│   │       ├── validators.dart
│   │       └── extensions.dart
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   │   ├── auth_repository.dart
│   │   │   │   └── models/
│   │   │   │       └── user_model.dart
│   │   │   ├── providers/
│   │   │   │   └── auth_provider.dart
│   │   │   └── presentation/
│   │   │       ├── screens/
│   │   │       │   ├── login_screen.dart
│   │   │       │   ├── register_screen.dart
│   │   │       │   └── splash_screen.dart
│   │   │       └── widgets/
│   │   │           ├── social_login_buttons.dart
│   │   │           └── auth_form_field.dart
│   │   │
│   │   ├── video/
│   │   │   ├── data/
│   │   │   │   ├── video_repository.dart
│   │   │   │   └── models/
│   │   │   │       └── video_model.dart
│   │   │   ├── providers/
│   │   │   │   └── video_provider.dart
│   │   │   └── presentation/
│   │   │       ├── screens/
│   │   │       │   ├── home_screen.dart
│   │   │       │   ├── video_upload_screen.dart
│   │   │       │   └── video_detail_screen.dart
│   │   │       └── widgets/
│   │   │           ├── video_card.dart
│   │   │           ├── upload_progress.dart
│   │   │           └── video_picker.dart
│   │   │
│   │   ├── analysis/
│   │   │   ├── data/
│   │   │   │   ├── analysis_repository.dart
│   │   │   │   └── models/
│   │   │   │       ├── analysis_model.dart
│   │   │   │       └── trick_model.dart
│   │   │   ├── providers/
│   │   │   │   └── analysis_provider.dart
│   │   │   └── presentation/
│   │   │       ├── screens/
│   │   │       │   ├── analysis_result_screen.dart
│   │   │       │   └── animation_viewer_screen.dart
│   │   │       └── widgets/
│   │   │           ├── score_card.dart
│   │   │           ├── trick_list.dart
│   │   │           ├── feedback_card.dart
│   │   │           └── share_button.dart
│   │   │
│   │   └── profile/
│   │       ├── data/
│   │       │   └── profile_repository.dart
│   │       ├── providers/
│   │       │   └── profile_provider.dart
│   │       └── presentation/
│   │           ├── screens/
│   │           │   ├── profile_screen.dart
│   │           │   └── settings_screen.dart
│   │           └── widgets/
│   │               └── profile_header.dart
│   │
│   └── shared/
│       ├── widgets/
│       │   ├── loading_overlay.dart
│       │   ├── error_view.dart
│       │   ├── empty_state.dart
│       │   └── custom_button.dart
│       └── utils/
│           └── snackbar_helper.dart
│
├── assets/
│   ├── images/
│   │   ├── logo.png
│   │   └── onboarding/
│   └── fonts/
│
├── pubspec.yaml
├── analysis_options.yaml
└── README.md
```

**Effort**: 30 minutes (creating directories and empty files)

---

### 2.3 Dependencies (pubspec.yaml)

**File**: `D:\Dev_Projects\Reride\frontend\pubspec.yaml`

```yaml
name: reride
description: AI-powered snowboard video analysis app
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.2.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter

  # State Management
  flutter_riverpod: ^2.5.1
  riverpod_annotation: ^2.3.5

  # Navigation
  go_router: ^14.0.0

  # Networking
  dio: ^5.4.3
  connectivity_plus: ^6.0.2

  # Local Storage
  flutter_secure_storage: ^9.0.0
  hive_flutter: ^1.1.0

  # Media
  image_picker: ^1.0.7
  video_player: ^2.8.3
  chewie: ^1.7.5
  permission_handler: ^11.3.0

  # Social Login
  kakao_flutter_sdk_user: ^1.9.0
  google_sign_in: ^6.2.1

  # Firebase (Push Notifications)
  firebase_core: ^2.27.0
  firebase_messaging: ^14.7.19

  # Sharing
  share_plus: ^7.2.2
  path_provider: ^2.1.2

  # UI Components
  cached_network_image: ^3.3.1
  shimmer: ^3.0.0
  flutter_svg: ^2.0.10
  lottie: ^3.1.0
  percent_indicator: ^4.2.3

  # Utilities
  intl: ^0.19.0
  freezed_annotation: ^2.4.1
  json_annotation: ^4.8.1
  equatable: ^2.0.5

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
  build_runner: ^2.4.8
  freezed: ^2.4.7
  json_serializable: ^6.7.1
  riverpod_generator: ^2.4.0
  mockito: ^5.4.4

flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/fonts/
```

**Effort**: 15 minutes

---

### 2.4 API Client Setup

**File**: `D:\Dev_Projects\Reride\frontend\lib\core\api\api_client.dart`

```dart
// Key implementation points:
// - Base URL configuration (dev/prod)
// - Request timeout settings
// - Auth token injection via interceptor
// - Error handling interceptor
// - Retry logic for network failures
// - Multipart upload support for videos

class ApiClient {
  late final Dio _dio;
  final SecureStorage _secureStorage;

  ApiClient(this._secureStorage) {
    _dio = Dio(BaseOptions(
      baseUrl: ApiEndpoints.baseUrl,
      connectTimeout: Duration(seconds: 30),
      receiveTimeout: Duration(seconds: 30),
    ));

    _dio.interceptors.addAll([
      AuthInterceptor(_secureStorage),
      ErrorInterceptor(),
      LogInterceptor(requestBody: true, responseBody: true),
    ]);
  }

  Future<Response<T>> get<T>(String path, {Map<String, dynamic>? params});
  Future<Response<T>> post<T>(String path, {dynamic data});
  Future<Response<T>> delete<T>(String path);
  Future<Response<T>> uploadFile(String path, File file, {void Function(int, int)? onProgress});
}
```

**File**: `D:\Dev_Projects\Reride\frontend\lib\core\api\api_endpoints.dart`

```dart
class ApiEndpoints {
  static const String baseUrl = 'http://localhost:8000/api/v1';  // Dev
  // static const String baseUrl = 'https://api.reride.com/api/v1';  // Prod

  // Auth
  static const String register = '/auth/register';
  static const String login = '/auth/login';
  static const String me = '/auth/me';
  static const String kakaoLogin = '/auth/kakao';
  static const String googleLogin = '/auth/google';

  // Videos
  static const String videos = '/videos';
  static const String uploadVideo = '/videos/upload';
  static String videoDetail(int id) => '/videos/$id';

  // Analysis
  static String startAnalysis(int videoId) => '/analysis/video/$videoId/start';
  static String analysisStatus(int videoId) => '/analysis/video/$videoId/status';
  static String analysisResult(int videoId) => '/analysis/video/$videoId';
}
```

**Effort**: 2 hours

---

### 2.5 State Management (Riverpod)

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\auth\providers\auth_provider.dart`

```dart
// Key providers:

@riverpod
class Auth extends _$Auth {
  @override
  FutureOr<User?> build() async {
    // Check for stored token on app start
    // Return User if valid token exists, null otherwise
  }

  Future<void> login(String email, String password);
  Future<void> register(String email, String username, String password);
  Future<void> loginWithKakao();
  Future<void> loginWithGoogle();
  Future<void> logout();
}

@riverpod
bool isAuthenticated(IsAuthenticatedRef ref) {
  return ref.watch(authProvider).valueOrNull != null;
}
```

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\video\providers\video_provider.dart`

```dart
@riverpod
class VideoList extends _$VideoList {
  @override
  FutureOr<List<Video>> build() async {
    return ref.read(videoRepositoryProvider).getVideos();
  }

  Future<void> refresh();
  Future<Video> uploadVideo(File file);
  Future<void> deleteVideo(int id);
}

@riverpod
class VideoUpload extends _$VideoUpload {
  @override
  UploadState build() => UploadState.idle();

  Future<void> upload(File file);  // Updates progress state
  void cancel();
}
```

**Effort**: 3 hours

---

### 2.6 Theme Configuration

**File**: `D:\Dev_Projects\Reride\frontend\lib\app\theme.dart`

```dart
class AppTheme {
  // Brand colors (snowboard/winter aesthetic)
  static const Color primary = Color(0xFF2E7D9B);      // Deep teal
  static const Color secondary = Color(0xFF64B5F6);   // Sky blue
  static const Color accent = Color(0xFFFF7043);       // Warm orange (for CTAs)
  static const Color background = Color(0xFFF5F7FA);  // Light gray
  static const Color surface = Colors.white;
  static const Color error = Color(0xFFE53935);

  static ThemeData get lightTheme => ThemeData(
    colorScheme: ColorScheme.light(
      primary: primary,
      secondary: secondary,
      error: error,
    ),
    // Typography, button styles, card themes, etc.
  );
}
```

**Effort**: 1 hour

---

### 2.7 Navigation (GoRouter)

**File**: `D:\Dev_Projects\Reride\frontend\lib\app\routes.dart`

```dart
final router = GoRouter(
  initialLocation: '/',
  redirect: (context, state) {
    final isAuthenticated = /* check auth state */;
    final isAuthRoute = state.matchedLocation.startsWith('/auth');

    if (!isAuthenticated && !isAuthRoute) return '/auth/login';
    if (isAuthenticated && isAuthRoute) return '/home';
    return null;
  },
  routes: [
    GoRoute(
      path: '/',
      redirect: (_, __) => '/splash',
    ),
    GoRoute(
      path: '/splash',
      builder: (_, __) => const SplashScreen(),
    ),
    ShellRoute(
      builder: (_, __, child) => AuthShell(child: child),
      routes: [
        GoRoute(path: '/auth/login', builder: (_, __) => const LoginScreen()),
        GoRoute(path: '/auth/register', builder: (_, __) => const RegisterScreen()),
      ],
    ),
    ShellRoute(
      builder: (_, __, child) => MainShell(child: child),  // With bottom nav
      routes: [
        GoRoute(path: '/home', builder: (_, __) => const HomeScreen()),
        GoRoute(path: '/upload', builder: (_, __) => const VideoUploadScreen()),
        GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
      ],
    ),
    GoRoute(
      path: '/video/:id',
      builder: (_, state) => VideoDetailScreen(id: int.parse(state.pathParameters['id']!)),
    ),
    GoRoute(
      path: '/analysis/:videoId',
      builder: (_, state) => AnalysisResultScreen(videoId: int.parse(state.pathParameters['videoId']!)),
    ),
    GoRoute(
      path: '/animation/:videoId',
      builder: (_, state) => AnimationViewerScreen(videoId: int.parse(state.pathParameters['videoId']!)),
    ),
  ],
);
```

**Effort**: 1 hour

---

### Phase 2 Summary

| Task | File/Directory | Effort | Dependencies |
|------|----------------|--------|--------------|
| 2.1 Create project | `frontend/` | 10m | None |
| 2.2 Project structure | All directories | 30m | 2.1 |
| 2.3 Dependencies | `pubspec.yaml` | 15m | 2.1 |
| 2.4 API Client | `core/api/*` | 2h | 2.3 |
| 2.5 State management | `**/providers/*` | 3h | 2.3, 2.4 |
| 2.6 Theme | `app/theme.dart` | 1h | 2.1 |
| 2.7 Navigation | `app/routes.dart` | 1h | 2.5 |

**Total Phase 2**: ~8 hours

---

## Phase 3: Flutter Screens

**Goal**: Build all UI screens with proper state management integration.

### 3.1 Splash Screen

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\auth\presentation\screens\splash_screen.dart`

**Functionality**:
- Show app logo with animation
- Check authentication status
- Navigate to login or home based on auth state
- Handle deep links

**Widgets used**:
- `Lottie` for logo animation
- `AnimatedOpacity` for fade effect

**Effort**: 1 hour

---

### 3.2 Login Screen

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\auth\presentation\screens\login_screen.dart`

**Functionality**:
- Email/password form with validation
- "Remember me" checkbox
- Social login buttons (Kakao, Google)
- Link to registration
- Loading state during authentication

**Widgets needed**:
- `AuthFormField` (custom text field with validation)
- `SocialLoginButtons` (Kakao + Google buttons)
- `CustomButton` (primary action button)

**Dependencies**: `auth_provider.dart`

**Effort**: 2 hours

---

### 3.3 Register Screen

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\auth\presentation\screens\register_screen.dart`

**Functionality**:
- Email, username, password, confirm password fields
- Real-time validation (email format, username availability, password strength)
- Terms of service checkbox
- Social registration option

**Effort**: 2 hours

---

### 3.4 Home Screen (Video List)

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\video\presentation\screens\home_screen.dart`

**Functionality**:
- Pull-to-refresh video list
- Video cards showing:
  - Thumbnail (first frame)
  - Filename
  - Status (uploaded/processing/completed/failed)
  - Created date
  - Analysis score (if completed)
- Empty state for new users
- FAB for upload
- Tap to view detail/analysis

**Widgets needed**:
- `VideoCard` (individual video item)
- `EmptyState` (no videos illustration)
- `Shimmer` (loading skeleton)

**Dependencies**: `video_provider.dart`

**Effort**: 3 hours

---

### 3.5 Video Upload Screen

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\video\presentation\screens\video_upload_screen.dart`

**Functionality**:
- Video picker (gallery or camera)
- Video preview before upload
- Upload progress indicator
- Cancel upload option
- Auto-navigate to home on success

**Widgets needed**:
- `VideoPicker` (gallery/camera selection)
- `UploadProgress` (circular progress with percentage)
- `VideoPreview` (playable preview)

**Flow**:
1. User taps "Select Video"
2. Opens gallery/camera picker
3. Shows preview with "Upload" button
4. Progress indicator during upload
5. Navigate to home, show success snackbar

**Dependencies**: `video_provider.dart`, `image_picker`, `video_player`

**Effort**: 3 hours

---

### 3.6 Video Detail Screen

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\video\presentation\screens\video_detail_screen.dart`

**Functionality**:
- Video player (original video)
- Video info (name, date, duration)
- Analysis status/progress
- "Start Analysis" button (if not started)
- "View Results" button (if completed)
- Delete video option

**Dependencies**: `video_provider.dart`, `analysis_provider.dart`, `chewie`

**Effort**: 2 hours

---

### 3.7 Analysis Result Screen

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\analysis\presentation\screens\analysis_result_screen.dart`

**Functionality**:
- Score display (overall, difficulty, stability)
- Detected tricks list with confidence
- Feedback text cards
- "View Animation" button
- "View Highlight" button
- Share button

**Widgets needed**:
- `ScoreCard` (circular progress with score)
- `TrickList` (list of detected tricks)
- `FeedbackCard` (collapsible feedback items)
- `ShareButton` (share to SNS)

**Dependencies**: `analysis_provider.dart`

**Effort**: 3 hours

---

### 3.8 Animation Viewer Screen

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\analysis\presentation\screens\animation_viewer_screen.dart`

**Functionality**:
- Full-screen video player for character animation
- Toggle between animation and highlight
- Download to device
- Share to Instagram/TikTok

**Widgets needed**:
- Full-screen `Chewie` player
- Download progress indicator
- Share sheet

**Dependencies**: `analysis_provider.dart`, `share_plus`, `path_provider`

**Effort**: 2 hours

---

### 3.9 Profile Screen

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\profile\presentation\screens\profile_screen.dart`

**Functionality**:
- User info (email, username, join date)
- Account type (free/premium)
- Total videos analyzed
- Settings link
- Logout button

**Widgets needed**:
- `ProfileHeader` (avatar, name, stats)
- Settings list tiles

**Effort**: 1.5 hours

---

### 3.10 Settings Screen

**File**: `D:\Dev_Projects\Reride\frontend\lib\features\profile\presentation\screens\settings_screen.dart`

**Functionality**:
- Push notification toggle
- Clear cache
- Terms of service link
- Privacy policy link
- App version
- Delete account

**Effort**: 1 hour

---

### Navigation Flow Diagram

```
┌─────────────┐
│   Splash    │
└──────┬──────┘
       │
       ▼
   ┌───────┐     ┌──────────┐
   │ Login │◄────│ Register │
   └───┬───┘     └──────────┘
       │
       ▼
┌──────────────────────────────────┐
│         Bottom Navigation         │
│  ┌──────┐  ┌────────┐  ┌───────┐ │
│  │ Home │  │ Upload │  │Profile│ │
│  └──┬───┘  └───┬────┘  └───────┘ │
└─────┼──────────┼─────────────────┘
      │          │
      ▼          │
┌────────────┐   │
│Video Detail│◄──┘
└─────┬──────┘
      │
      ▼
┌──────────────┐
│Analysis Result│
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│Animation Viewer  │
└──────────────────┘
```

---

### Phase 3 Summary

| Task | Screen | Effort | Dependencies |
|------|--------|--------|--------------|
| 3.1 | Splash Screen | 1h | 2.7 |
| 3.2 | Login Screen | 2h | 2.5, 2.7 |
| 3.3 | Register Screen | 2h | 2.5, 2.7 |
| 3.4 | Home Screen | 3h | 2.5, 3.2 |
| 3.5 | Video Upload Screen | 3h | 2.5, 3.4 |
| 3.6 | Video Detail Screen | 2h | 3.4 |
| 3.7 | Analysis Result Screen | 3h | 3.6 |
| 3.8 | Animation Viewer Screen | 2h | 3.7 |
| 3.9 | Profile Screen | 1.5h | 2.5 |
| 3.10 | Settings Screen | 1h | 3.9 |

**Total Phase 3**: ~20.5 hours

---

## Phase 4: Integration & Testing

### 4.1 Backend-Frontend API Integration

**Test Scenarios**:

| Scenario | Steps | Expected Result |
|----------|-------|-----------------|
| User Registration | Fill form → Submit | Account created, auto-login, navigate to home |
| User Login | Enter credentials → Submit | Token stored, navigate to home |
| Social Login (Kakao) | Tap Kakao button → OAuth flow | Account created/linked, navigate to home |
| Video Upload | Select video → Upload | Progress shown, video appears in list |
| Start Analysis | Tap "Analyze" on video | Status changes to "processing", progress updates |
| View Analysis | Tap completed video | Scores and tricks displayed |
| View Animation | Tap "View Animation" | Video plays in full-screen |
| Share to SNS | Tap share → Select platform | Share sheet opens, video shared |
| Logout | Tap logout → Confirm | Token cleared, navigate to login |

**Effort**: 4 hours

---

### 4.2 Error Handling

**File**: `D:\Dev_Projects\Reride\frontend\lib\core\api\interceptors\error_interceptor.dart`

Handle these cases:
- Network timeout → Show retry option
- 401 Unauthorized → Clear token, navigate to login
- 400 Bad Request → Show validation errors
- 500 Server Error → Show generic error with retry
- No network → Show offline state, use cached data

**Effort**: 2 hours

---

### 4.3 Offline Support

**Implementation**:
- Cache video list in Hive
- Cache analysis results in Hive
- Show cached data when offline
- Queue uploads for when online
- Sync indicator in UI

**Files**:
- `D:\Dev_Projects\Reride\frontend\lib\core\storage\local_storage.dart`
- Update providers to check connectivity

**Effort**: 3 hours

---

### 4.4 Push Notifications

**Setup**:
1. Configure Firebase project
2. Add `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)
3. Implement `FirebaseMessaging` in `main.dart`
4. Handle notification tap → Navigate to analysis result

**File**: `D:\Dev_Projects\Reride\frontend\lib\main.dart`

**Effort**: 2 hours

---

### 4.5 E2E Test Scenarios

**Critical Paths to Test**:

1. **New User Flow**:
   ```
   Register → Upload Video → Start Analysis → Wait for Completion → View Results → Share
   ```

2. **Returning User Flow**:
   ```
   Login → View Past Analyses → Re-share Animation
   ```

3. **Error Recovery Flow**:
   ```
   Upload → Network Error → Retry → Success
   ```

4. **Offline Flow**:
   ```
   Go offline → View cached videos → View cached analysis → Go online → Sync
   ```

**Effort**: 4 hours (manual testing) + 6 hours (automated tests)

---

### Phase 4 Summary

| Task | Description | Effort |
|------|-------------|--------|
| 4.1 | API Integration Testing | 4h |
| 4.2 | Error Handling | 2h |
| 4.3 | Offline Support | 3h |
| 4.4 | Push Notifications | 2h |
| 4.5 | E2E Testing | 10h |

**Total Phase 4**: ~21 hours

---

## Task Dependency Graph

```
Phase 1 (Backend)
├── 1.1 Services dir ─────────┬─────────┬─────────┬─────────┐
│                             │         │         │         │
├── 1.7 New models ───────────┤         │         │         │
│                             ▼         ▼         ▼         ▼
│                          1.2 Auth  1.3 Video  1.4 Analysis  1.5 Notification
│                             │         │         │         │
│                             └────┬────┴────┬────┘         │
│                                  ▼         ▼              │
├── 1.8 New schemas ──────────────►1.6 Update API Routes◄───┘
│
│
Phase 2 (Flutter Setup)
├── 2.1 Create project ───┬───────┬───────┬───────┐
│                         │       │       │       │
│                         ▼       ▼       ▼       ▼
│                      2.2 Structure  2.3 Deps  2.6 Theme
│                         │       │
│                         │       ▼
│                         │    2.4 API Client
│                         │       │
│                         └───┬───┘
│                             ▼
│                          2.5 State Management
│                             │
│                             ▼
│                          2.7 Navigation
│
│
Phase 3 (Screens) ──────────────────────────────────────────────
│                                                               │
│   ┌─────────────────────────────────────────────────────────┐ │
│   │                                                         │ │
│   │  3.1 Splash ──► 3.2 Login ──► 3.3 Register             │ │
│   │                    │                                    │ │
│   │                    ▼                                    │ │
│   │                 3.4 Home ──► 3.5 Upload                 │ │
│   │                    │                                    │ │
│   │                    ▼                                    │ │
│   │              3.6 Video Detail                           │ │
│   │                    │                                    │ │
│   │                    ▼                                    │ │
│   │              3.7 Analysis Result                        │ │
│   │                    │                                    │ │
│   │                    ▼                                    │ │
│   │              3.8 Animation Viewer                       │ │
│   │                                                         │ │
│   │  3.9 Profile ──► 3.10 Settings                         │ │
│   │                                                         │ │
│   └─────────────────────────────────────────────────────────┘ │
│                                                               │
Phase 4 (Integration)
├── 4.1 API Integration ◄─── Phase 1 + Phase 3
├── 4.2 Error Handling
├── 4.3 Offline Support
├── 4.4 Push Notifications ◄─── 1.5 Notification Service
└── 4.5 E2E Testing ◄─── All above
```

---

## Total Effort Summary

| Phase | Description | Effort |
|-------|-------------|--------|
| 1 | Backend Services Layer | 13h |
| 2 | Flutter App Setup | 8h |
| 3 | Flutter Screens | 20.5h |
| 4 | Integration & Testing | 21h |
| **Total** | | **62.5 hours** |

**Estimated Calendar Time**: 4-6 weeks (1 developer, part-time)

---

## Quick Start Commands

### Backend Development
```bash
cd D:\Dev_Projects\Reride
docker-compose up -d db redis
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Start Celery Worker
```bash
cd D:\Dev_Projects\Reride\backend
celery -A app.workers.analyze_video worker --loglevel=info
```

### Flutter Development
```bash
cd D:\Dev_Projects\Reride\frontend
flutter pub get
flutter run
```

---

## Configuration Files Needed

1. **Backend `.env`**:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/reride
   REDIS_URL=redis://localhost:6379/0
   SECRET_KEY=your-secret-key-here
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   ```

2. **Flutter Firebase Config**:
   - `frontend/android/app/google-services.json`
   - `frontend/ios/Runner/GoogleService-Info.plist`

3. **Social Login Keys**:
   - Kakao: Add to `AndroidManifest.xml` and `Info.plist`
   - Google: Configure in Firebase console

---

## Next Steps (Recommended Order)

1. **[IMMEDIATE]** Create services directory and `__init__.py`
2. **[IMMEDIATE]** Implement `video_service.py` (simplest, unblocks testing)
3. **[IMMEDIATE]** Initialize Flutter project
4. **[WEEK 1]** Complete Phase 1 (Backend Services)
5. **[WEEK 2]** Complete Phase 2 (Flutter Setup)
6. **[WEEK 2-4]** Complete Phase 3 (Screens)
7. **[WEEK 4-5]** Complete Phase 4 (Integration)
8. **[WEEK 5-6]** Bug fixes and polish
