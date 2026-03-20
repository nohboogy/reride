import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/router.dart';
import '../../core/theme.dart';
import '../auth/providers/auth_provider.dart';
import 'providers/profile_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(profileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('PROFILE'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new),
          onPressed: () => context.pop(),
        ),
      ),
      body: profileAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => _ErrorView(
          message: err.toString(),
          onRetry: () => ref.read(profileProvider.notifier).refresh(),
        ),
        data: (profileState) {
          if (profileState.error != null && profileState.profile == null) {
            return _ErrorView(
              message: profileState.error!,
              onRetry: () => ref.read(profileProvider.notifier).refresh(),
            );
          }
          return _ProfileBody(profileState: profileState);
        },
      ),
    );
  }
}

class _ProfileBody extends ConsumerWidget {
  final ProfileState profileState;
  const _ProfileBody({required this.profileState});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = profileState.profile;
    final username = profile?['username'] as String? ??
        profile?['name'] as String? ??
        'Rider';
    final email =
        profile?['email'] as String? ?? 'rider@reride.app';
    final karma = profile?['karma'] as int? ?? 0;
    final analysisCount =
        profile?['analysis_count'] as int? ?? 0;

    return SafeArea(
      child: RefreshIndicator(
        color: RerideColors.primaryLight,
        backgroundColor: RerideColors.surfaceCard,
        onRefresh: () => ref.read(profileProvider.notifier).refresh(),
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const SizedBox(height: 16),

              // ── Avatar ───────────────────────────────────────────────
              Container(
                width: 96,
                height: 96,
                decoration: BoxDecoration(
                  gradient: RerideColors.primaryGradient,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: RerideColors.primary.withOpacity(0.4),
                      blurRadius: 20,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.person,
                  color: Colors.white,
                  size: 48,
                ),
              ),
              const SizedBox(height: 16),

              Text(
                username,
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 4),
              Text(
                email,
                style: Theme.of(context).textTheme.bodyMedium,
              ),

              // ── Soft error banner ─────────────────────────────────────
              if (profileState.error != null) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: RerideColors.error.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                        color: RerideColors.error.withOpacity(0.3)),
                  ),
                  child: Text(
                    profileState.error!,
                    style: const TextStyle(
                        color: RerideColors.error, fontSize: 12),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],

              const SizedBox(height: 32),

              // ── Stats Row ────────────────────────────────────────────
              Row(
                children: [
                  _StatCard(
                      label: 'Analyses',
                      value: analysisCount.toString()),
                  const SizedBox(width: 12),
                  _StatCard(
                      label: 'Karma',
                      value: karma.toString()),
                  const SizedBox(width: 12),
                  _StatCard(
                      label: 'Best Score',
                      value: profile?['best_score'] != null
                          ? (profile!['best_score'] as num)
                              .toStringAsFixed(1)
                          : '—'),
                ],
              ),
              const SizedBox(height: 32),

              // ── Settings List ────────────────────────────────────────
              _SettingsItem(
                icon: Icons.notifications_outlined,
                label: 'Notifications',
                onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('준비 중인 기능입니다')),
                ),
              ),
              _SettingsItem(
                icon: Icons.language_outlined,
                label: 'Language',
                onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('준비 중인 기능입니다')),
                ),
              ),
              _SettingsItem(
                icon: Icons.help_outline,
                label: 'Help & Feedback',
                onTap: () => ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('준비 중인 기능입니다')),
                ),
              ),
              const Divider(height: 24),
              _SettingsItem(
                icon: Icons.logout,
                label: 'Sign Out',
                destructive: true,
                onTap: () => _confirmSignOut(context, ref),
              ),

              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _confirmSignOut(
      BuildContext context, WidgetRef ref) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: RerideColors.surfaceCard,
        title: const Text('로그아웃'),
        content: const Text('정말 로그아웃 하시겠습니까?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(
                foregroundColor: RerideColors.error),
            child: const Text('로그아웃'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await ref.read(authProvider.notifier).logout();
      if (context.mounted) {
        context.go(AppRoutes.login);
      }
    }
  }
}

// ── Error view ────────────────────────────────────────────────────────────────

class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;
  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline,
                size: 64, color: RerideColors.error),
            const SizedBox(height: 16),
            Text('프로필 로드 실패',
                style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('다시 시도'),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Stat Card ──────────────────────────────────────────────────────────────────

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  const _StatCard({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: RerideColors.surfaceCard,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: RerideColors.divider),
        ),
        child: Column(
          children: [
            Text(
              value,
              style: const TextStyle(
                color: RerideColors.primaryLight,
                fontSize: 22,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 4),
            Text(label, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}

// ── Settings Item ─────────────────────────────────────────────────────────────

class _SettingsItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final bool destructive;
  final VoidCallback onTap;

  const _SettingsItem({
    required this.icon,
    required this.label,
    required this.onTap,
    this.destructive = false,
  });

  @override
  Widget build(BuildContext context) {
    final color =
        destructive ? RerideColors.error : RerideColors.onBackground;
    return ListTile(
      leading: Icon(icon, color: color),
      title: Text(label,
          style: TextStyle(
              color: color, fontWeight: FontWeight.w500)),
      trailing: destructive
          ? null
          : const Icon(Icons.chevron_right,
              color: RerideColors.primaryLight),
      onTap: onTap,
    );
  }
}
