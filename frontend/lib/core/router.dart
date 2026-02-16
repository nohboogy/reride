import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/home/home_screen.dart';
import '../features/upload/screens/upload_screen.dart';
import '../features/analysis/analysis_screen.dart';
import '../features/profile/profile_screen.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/auth/screens/register_screen.dart';
import '../features/auth/providers/auth_provider.dart';

// ── Route paths ──────────────────────────────────────────────────────────────
abstract class AppRoutes {
  static const String home = '/';
  static const String upload = '/upload';
  static const String analysis = '/analysis/:id';
  static const String profile = '/profile';
  static const String login = '/login';
  static const String register = '/register';

  static String analysisPath(String id) => '/analysis/$id';
}

// ── Routes that do NOT require authentication ─────────────────────────────────
const _publicRoutes = {AppRoutes.login, AppRoutes.register};

// ── GoRouter instance ────────────────────────────────────────────────────────
// Built lazily via provider so we can read authProvider for redirect logic.
final routerProvider = Provider<GoRouter>((ref) {
  final authListenable = _AuthListenable(ref);

  return GoRouter(
    initialLocation: AppRoutes.home,
    debugLogDiagnostics: true,
    refreshListenable: authListenable,

    // ── Auth redirect guard ───────────────────────────────────────────────
    redirect: (context, state) {
      final auth = ref.read(authProvider);
      // Still loading initial auth state → wait (no redirect)
      if (auth.isLoading) return null;

      final isOnPublicRoute = _publicRoutes.contains(state.matchedLocation);

      if (!auth.isAuthenticated && !isOnPublicRoute) {
        // Not logged in → go to login, remember where they were going
        final from = state.uri.toString();
        return '${AppRoutes.login}?from=${Uri.encodeComponent(from)}';
      }

      if (auth.isAuthenticated && isOnPublicRoute) {
        // Already logged in → bounce to home
        return AppRoutes.home;
      }

      return null; // No redirect
    },

    routes: [
      // ── Public routes ───────────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.login,
        name: 'login',
        pageBuilder: (context, state) => _fadeTransition(
          state,
          const LoginScreen(),
        ),
      ),
      GoRoute(
        path: AppRoutes.register,
        name: 'register',
        pageBuilder: (context, state) => _slideTransition(
          state,
          const RegisterScreen(),
        ),
      ),

      // ── Protected routes ────────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.home,
        name: 'home',
        pageBuilder: (context, state) => _fadeTransition(
          state,
          const HomeScreen(),
        ),
      ),
      GoRoute(
        path: AppRoutes.upload,
        name: 'upload',
        pageBuilder: (context, state) => _slideTransition(
          state,
          const UploadScreen(),
        ),
      ),
      GoRoute(
        path: AppRoutes.analysis,
        name: 'analysis',
        pageBuilder: (context, state) {
          final id = state.pathParameters['id'] ?? '';
          return _slideTransition(state, AnalysisScreen(analysisId: id));
        },
      ),
      GoRoute(
        path: AppRoutes.profile,
        name: 'profile',
        pageBuilder: (context, state) => _fadeTransition(
          state,
          const ProfileScreen(),
        ),
      ),
    ],

    // ── Global error page ────────────────────────────────────────────────
    errorPageBuilder: (context, state) => MaterialPage(
      key: state.pageKey,
      child: Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.redAccent),
              const SizedBox(height: 16),
              Text(
                '페이지를 찾을 수 없습니다',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 8),
              Text(state.error?.message ?? ''),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => context.go(AppRoutes.home),
                child: const Text('홈으로'),
              ),
            ],
          ),
        ),
      ),
    ),
  );
});

// ── Convenience getter for non-Riverpod contexts ──────────────────────────────
// Still provided for backward compat with older screens that import `appRouter`
GoRouter get appRouter => throw UnimplementedError(
      'Use routerProvider instead: ref.watch(routerProvider)',
    );

// ── Transition helpers ───────────────────────────────────────────────────────
CustomTransitionPage<void> _fadeTransition(GoRouterState state, Widget child) =>
    CustomTransitionPage<void>(
      key: state.pageKey,
      child: child,
      transitionDuration: const Duration(milliseconds: 300),
      transitionsBuilder: (_, animation, __, child) =>
          FadeTransition(opacity: animation, child: child),
    );

CustomTransitionPage<void> _slideTransition(GoRouterState state, Widget child) =>
    CustomTransitionPage<void>(
      key: state.pageKey,
      child: child,
      transitionDuration: const Duration(milliseconds: 350),
      transitionsBuilder: (_, animation, __, child) => SlideTransition(
        position: animation.drive(
          Tween(begin: const Offset(1.0, 0.0), end: Offset.zero)
              .chain(CurveTween(curve: Curves.easeOutCubic)),
        ),
        child: child,
      ),
    );

// ── Auth Listenable ──────────────────────────────────────────────────────────
// Notifies GoRouter when auth state changes so redirect runs again
class _AuthListenable extends ChangeNotifier {
  _AuthListenable(Ref ref) {
    ref.listen<AuthState>(authProvider, (_, __) {
      notifyListeners();
    });
  }
}
