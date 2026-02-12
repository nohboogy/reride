# Reride Frontend (Flutter)

## Prerequisites

Flutter SDK must be installed before initializing this project.

### Installing Flutter

1. Download Flutter SDK from: https://flutter.dev/docs/get-started/install
2. Extract to a location (e.g., `C:\flutter`)
3. Add Flutter to PATH:
   - Windows: Add `C:\flutter\bin` to System Environment Variables
4. Verify installation: `flutter --version`
5. Run Flutter doctor: `flutter doctor`

## Project Initialization

Once Flutter is installed, initialize the project:

```bash
cd frontend
flutter create --org com.reride --project-name reride_app .
```

## Project Structure (Planned)

```
lib/
├── main.dart                 # App entry point
├── core/
│   ├── config/              # App configuration
│   ├── constants/           # Constants and enums
│   └── themes/              # Theme configuration
├── data/
│   ├── models/              # Data models
│   ├── repositories/        # Data repositories
│   └── services/            # API services
├── presentation/
│   ├── screens/             # Screen widgets
│   │   ├── auth/           # Authentication screens
│   │   ├── home/           # Home screen
│   │   ├── video/          # Video upload/list
│   │   └── analysis/       # Analysis results
│   ├── widgets/            # Reusable widgets
│   └── providers/          # State management (Riverpod/Provider)
└── utils/                  # Utility functions
```

## Key Dependencies (To be added)

```yaml
dependencies:
  flutter:
    sdk: flutter

  # State Management
  flutter_riverpod: ^2.4.0

  # HTTP & API
  http: ^1.1.0
  dio: ^5.3.3

  # Storage
  shared_preferences: ^2.2.2
  flutter_secure_storage: ^9.0.0

  # Video
  video_player: ^2.7.2
  image_picker: ^1.0.4

  # UI
  google_fonts: ^6.1.0
  flutter_svg: ^2.0.9

  # Utilities
  intl: ^0.18.1
```

## Backend Integration

The app will connect to the FastAPI backend running at:
- Development: `http://localhost:8000/api`
- Production: TBD

### API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/videos/upload` - Upload video
- `GET /api/videos/` - List user videos
- `GET /api/videos/{id}` - Get video details
- `GET /api/analysis/video/{id}` - Get analysis results

## Development Workflow

1. Install Flutter SDK
2. Initialize project: `flutter create .`
3. Install dependencies: `flutter pub get`
4. Run on emulator/device: `flutter run`
5. Build for production:
   - Android: `flutter build apk`
   - iOS: `flutter build ios`

## Next Steps

1. Install Flutter SDK
2. Run `flutter create` command above
3. Add dependencies to `pubspec.yaml`
4. Implement core structure
5. Create authentication screens
6. Implement video upload functionality
7. Build analysis results display
