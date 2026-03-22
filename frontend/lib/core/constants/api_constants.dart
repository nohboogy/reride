/// API 엔드포인트 상수
class ApiConstants {
  ApiConstants._();

  // Base URLs
  static const String baseUrlDev = 'http://localhost:8000';
  static const String baseUrlProd = 'https://api.reride.app';

  // 현재 환경에 따라 변경
  static const String baseUrl = baseUrlDev;

  // API 버전
  static const String apiVersion = '/api/v1';

  // 엔드포인트
  static const String auth = '$apiVersion/auth';
  static const String login = '$auth/login';
  static const String register = '$auth/register';
  static const String refreshToken = '$auth/refresh';

  static const String videos = '$apiVersion/videos';
  static const String uploadVideo = '$videos/upload';

  static const String analysis = '$apiVersion/analysis';

  static const String users = '$apiVersion/users';
  static const String profile = '$users/me';

  // 타임아웃 설정
  static const int connectTimeout = 30000;  // ms
  static const int receiveTimeout = 60000;  // ms (영상 업로드용 길게 설정)
  static const int sendTimeout = 120000;    // ms

  // 폴링 간격 (분석 상태 확인)
  static const int analysisPollingInterval = 3000; // ms
  static const int analysisMaxPollingRetries = 600;

  // Secure Storage Keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userIdKey = 'user_id';
}
