import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// ── Base URL config ──────────────────────────────────────────────────────────
// Set via environment variable at build time:
//   flutter run --dart-define=API_BASE_URL=https://api.reride.app
const _kBaseUrl =
    String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:8000');

// ── Data models ───────────────────────────────────────────────────────────────

/// Represents a submitted analysis (upload response or list item).
class VideoItem {
  final String id;
  final String status;
  final int videoId;
  final double? overallScore;
  final double? difficultyScore;
  final double? stabilityScore;
  final dynamic feedbackText;
  final List<dynamic>? tricksDetected;
  final String? animationUrl;
  final String? highlightUrl;
  final String? overlayUrl;
  final String createdAt;

  const VideoItem({
    required this.id,
    required this.status,
    required this.videoId,
    this.overallScore,
    this.difficultyScore,
    this.stabilityScore,
    this.feedbackText,
    this.tricksDetected,
    this.animationUrl,
    this.highlightUrl,
    this.overlayUrl,
    required this.createdAt,
  });

  factory VideoItem.fromJson(Map<String, dynamic> json) => VideoItem(
        id: json['id']?.toString() ?? '',
        status: json['status'] ?? 'pending',
        videoId: json['video_id'] ?? 0,
        overallScore: (json['overall_score'] as num?)?.toDouble(),
        difficultyScore: (json['difficulty_score'] as num?)?.toDouble(),
        stabilityScore: (json['stability_score'] as num?)?.toDouble(),
        feedbackText: json['feedback_text'],
        tricksDetected: json['tricks_detected'] is List
            ? List<dynamic>.from(json['tricks_detected'] as List)
            : null,
        animationUrl: json['animation_url'] as String?,
        highlightUrl: json['highlight_url'] as String?,
        overlayUrl: json['overlay_url'] as String?,
        createdAt: json['created_at'] ?? '',
      );
}

/// Lightweight status snapshot (status + progress) returned by getAnalysisStatus.
class AnalysisStatus {
  final String id;
  final String status; // pending | processing | done | failed
  final int videoId;
  final int? progress; // 0-100 (derived)
  final String? message;

  const AnalysisStatus({
    required this.id,
    required this.status,
    required this.videoId,
    this.progress,
    this.message,
  });

  factory AnalysisStatus.fromJson(Map<String, dynamic> json) {
    final st = json['status'] as String? ?? 'pending';
    final int prog = st == 'done'
        ? 100
        : st == 'processing'
            ? 50
            : 0;
    return AnalysisStatus(
      id: json['id']?.toString() ?? '',
      status: st,
      videoId: json['video_id'] ?? 0,
      progress: prog,
      message: null,
    );
  }
}

/// Full analysis result with scores and feedback, mapped for the result screen.
class AnalysisResult {
  final String id;
  final double overallScore;
  final String? trickName;
  final Map<String, double> detailedScores;
  final List<String> feedback;
  final DateTime analyzedAt;
  final String? animationUrl;
  final String? highlightUrl;
  final String? overlayUrl;

  const AnalysisResult({
    required this.id,
    required this.overallScore,
    this.trickName,
    required this.detailedScores,
    required this.feedback,
    required this.analyzedAt,
    this.animationUrl,
    this.highlightUrl,
    this.overlayUrl,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    // Build detailed scores map from backend fields
    final Map<String, double> scores = {};
    if (json['difficulty_score'] != null) {
      scores['난이도'] = (json['difficulty_score'] as num).toDouble();
    }
    if (json['stability_score'] != null) {
      scores['안정성'] = (json['stability_score'] as num).toDouble();
    }

    // Extract first trick name if available
    String? trickName;
    final tricks = json['tricks_detected'];
    if (tricks is List && tricks.isNotEmpty) {
      final first = tricks.first;
      if (first is Map) {
        trickName = (first['trick_type'] ?? first['type']) as String?;
      }
    }

    // Normalise feedback_text (backend stores as JSON list or null)
    final List<String> feedbackList = [];
    final raw = json['feedback_text'];
    if (raw is List) {
      feedbackList.addAll(raw.map((e) => e.toString()));
    } else if (raw is String && raw.isNotEmpty) {
      feedbackList.add(raw);
    }

    return AnalysisResult(
      id: json['id']?.toString() ?? '',
      overallScore: (json['overall_score'] as num?)?.toDouble() ?? 0.0,
      trickName: trickName,
      detailedScores: scores,
      feedback: feedbackList,
      analyzedAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      animationUrl: json['animation_url'] as String?,
      highlightUrl: json['highlight_url'] as String?,
      overlayUrl: json['overlay_url'] as String?,
    );
  }
}

// ── ApiService ───────────────────────────────────────────────────────────────
class ApiService {
  ApiService._() : _dio = _buildDio();

  static final ApiService instance = ApiService._();

  final Dio _dio;

  static Dio _buildDio() {
    final dio = Dio(
      BaseOptions(
        baseUrl: _kBaseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 60),
        sendTimeout: const Duration(seconds: 60),
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      ),
    );

    // Logging interceptor (debug only)
    assert(() {
      dio.interceptors.add(
        LogInterceptor(
          requestBody: true,
          responseBody: true,
          logPrint: (obj) => print('[ApiService] $obj'),
        ),
      );
      return true;
    }());

    dio.interceptors.add(_AuthInterceptor());

    return dio;
  }

  // ── Auth token helper ──────────────────────────────────────────────────────
  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  void clearAuthToken() {
    _dio.options.headers.remove('Authorization');
  }

  // ── Analysis endpoints ─────────────────────────────────────────────────────

  /// Upload a video file and auto-trigger analysis.
  /// Uses XFile bytes for cross-platform (web + mobile) compatibility.
  Future<VideoItem> uploadVideo({
    required String filePath,
    String? title,
    String? location,
    void Function(int sent, int total)? onSendProgress,
    List<int>? fileBytes,       // web에서 XFile.readAsBytes() 결과
    String? fileName,
  }) async {
    final MultipartFile multipart;
    if (fileBytes != null) {
      // Web: 바이트 직접 사용
      multipart = MultipartFile.fromBytes(
        fileBytes,
        filename: fileName ?? 'video.mp4',
      );
    } else {
      // Mobile/Desktop: 파일 경로 사용
      multipart = await MultipartFile.fromFile(
        filePath,
        filename: fileName ?? filePath.split('/').last,
      );
    }

    final formData = FormData.fromMap({
      'file': multipart,
      if (title != null) 'title': title,
      if (location != null) 'location': location,
    });

    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/analyses',
      data: formData,
      onSendProgress: onSendProgress,
    );
    return VideoItem.fromJson(response.data ?? {});
  }

  /// Get analysis status (pending / processing / done / failed).
  Future<AnalysisStatus> getAnalysisStatus(String analysisId) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/analyses/$analysisId',
    );
    return AnalysisStatus.fromJson(response.data ?? {});
  }

  /// Get completed analysis result with scores and feedback.
  Future<AnalysisResult> getAnalysisResult(String analysisId) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/analyses/$analysisId',
    );
    return AnalysisResult.fromJson(response.data ?? {});
  }

  /// Delete an analysis by ID.
  Future<void> deleteAnalysis(String analysisId) async {
    await _dio.delete('/api/v1/analyses/$analysisId');
  }

  /// List analyses for the current user with pagination.
  Future<List<VideoItem>> listAnalyses({int page = 1, int pageSize = 20}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/api/v1/analyses',
      queryParameters: {'skip': (page - 1) * pageSize, 'limit': pageSize},
    );
    final items = (response.data?['items'] as List?) ?? [];
    return items
        .whereType<Map<String, dynamic>>()
        .map(VideoItem.fromJson)
        .toList();
  }

  // ── User / Profile endpoints ───────────────────────────────────────────────

  Future<Map<String, dynamic>> getProfile() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/v1/auth/me');
    return response.data ?? {};
  }

  Future<Map<String, dynamic>> updateProfile(
      Map<String, dynamic> payload) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/api/v1/auth/me',
      data: payload,
    );
    return response.data ?? {};
  }

  // ── Auth endpoints ─────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/auth/login',
      data: {'email': email, 'password': password},
    );
    return response.data ?? {};
  }

  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String username,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/v1/auth/register',
      data: {
        'email': email,
        'password': password,
        'username': username,
      },
    );
    return response.data ?? {};
  }

  Future<void> logout() async {
    try {
      await _dio.post('/api/v1/auth/logout');
    } catch (_) {}
    clearAuthToken();
  }
}

// ── Riverpod provider ────────────────────────────────────────────────────────

final apiServiceProvider = Provider<ApiService>((ref) => ApiService.instance);

// ── Auth interceptor ─────────────────────────────────────────────────────────
class _AuthInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (err.response?.statusCode == 401) {
      // TODO: trigger re-auth flow via Riverpod notifier
    }
    handler.next(err);
  }
}
