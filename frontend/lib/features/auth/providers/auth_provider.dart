import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../../services/api_service.dart';

// ── Storage key constants ─────────────────────────────────────────────────
const _kTokenKey = 'auth_token';

// ── Auth state ────────────────────────────────────────────────────────────

class AuthState {
  final bool isAuthenticated;
  final bool isLoading;
  final String? error;
  final String? token;
  final Map<String, dynamic>? user;

  const AuthState({
    this.isAuthenticated = false,
    this.isLoading = false,
    this.error,
    this.token,
    this.user,
  });

  AuthState copyWith({
    bool? isAuthenticated,
    bool? isLoading,
    String? error,
    String? token,
    Map<String, dynamic>? user,
    bool clearError = false,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      token: token ?? this.token,
      user: user ?? this.user,
    );
  }
}

// ── Auth Notifier ─────────────────────────────────────────────────────────

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier(this._ref) : super(const AuthState()) {
    _init();
  }

  final Ref _ref;
  final _storage = const FlutterSecureStorage();

  /// On startup: read saved token and validate it
  Future<void> _init() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final token = await _storage.read(key: _kTokenKey);
      if (token != null && token.isNotEmpty) {
        final api = _ref.read(apiServiceProvider);
        api.setAuthToken(token);
        // Verify token is still valid
        final profile = await api.getProfile();
        state = state.copyWith(
          isAuthenticated: true,
          isLoading: false,
          token: token,
          user: profile,
        );
      } else {
        state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      // Token expired or invalid
      await _storage.delete(key: _kTokenKey);
      _ref.read(apiServiceProvider).clearAuthToken();
      state = state.copyWith(isLoading: false);
    }
  }

  /// Login with email + password
  Future<bool> login({required String email, required String password}) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final api = _ref.read(apiServiceProvider);
      final result = await api.login(email: email, password: password);
      final token = result['access_token'] as String?;
      if (token == null) throw Exception('로그인에 실패했습니다.');
      await _storage.write(key: _kTokenKey, value: token);
      api.setAuthToken(token);
      final profile = await api.getProfile();
      state = state.copyWith(
        isAuthenticated: true,
        isLoading: false,
        token: token,
        user: profile,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: _parseError(e),
      );
      return false;
    }
  }

  /// Register a new account
  Future<bool> register({
    required String email,
    required String password,
    required String username,
  }) async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final api = _ref.read(apiServiceProvider);
      await api.register(
        email: email,
        password: password,
        username: username,
      );
      // Auto-login after register
      return await login(email: email, password: password);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: _parseError(e),
      );
      return false;
    }
  }

  /// Logout
  Future<void> logout() async {
    try {
      await _ref.read(apiServiceProvider).logout();
    } catch (_) {}
    await _storage.delete(key: _kTokenKey);
    state = const AuthState();
  }

  /// Clear error message
  void clearError() => state = state.copyWith(clearError: true);

  String _parseError(Object e) {
    final msg = e.toString();
    if (msg.contains('401') || msg.contains('Unauthorized')) {
      return '이메일 또는 비밀번호가 올바르지 않습니다.';
    }
    if (msg.contains('409') || msg.contains('already')) {
      return '이미 사용 중인 이메일입니다.';
    }
    if (msg.contains('SocketException') || msg.contains('Connection')) {
      return '서버에 연결할 수 없습니다. 네트워크를 확인하세요.';
    }
    return '오류가 발생했습니다. 다시 시도해주세요.';
  }
}

// ── Providers ─────────────────────────────────────────────────────────────

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>(
  (ref) => AuthNotifier(ref),
);
