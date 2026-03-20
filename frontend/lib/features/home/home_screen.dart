import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/router.dart';
import '../../core/theme.dart';
import 'providers/home_provider.dart';
import '../../services/api_service.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncState = ref.watch(homeProvider);
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('RERIDE'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outline),
            tooltip: 'Profile',
            onPressed: () => context.push(AppRoutes.profile),
          ),
        ],
      ),
      body: SafeArea(
        child: asyncState.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (err, _) => _ErrorView(
            message: err.toString(),
            onRetry: () => ref.read(homeProvider.notifier).refresh(),
          ),
          data: (homeState) {
            // Show API-level error banner but still render content
            return RefreshIndicator(
              color: RerideColors.primaryLight,
              backgroundColor: RerideColors.surfaceCard,
              onRefresh: () => ref.read(homeProvider.notifier).refresh(),
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.symmetric(
                    horizontal: 24, vertical: 32),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    // ── Hero ───────────────────────────────────────────
                    _HeroBanner(),
                    const SizedBox(height: 40),

                    // ── Upload CTA ─────────────────────────────────────
                    _UploadButton(),
                    const SizedBox(height: 40),

                    // ── Error banner (soft) ────────────────────────────
                    if (homeState.error != null) ...[
                      _ErrorBanner(message: homeState.error!),
                      const SizedBox(height: 16),
                    ],

                    // ── Recent Sessions ────────────────────────────────
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text('Recent Sessions',
                          style: textTheme.titleLarge),
                    ),
                    const SizedBox(height: 16),

                    homeState.videos.isEmpty
                        ? _EmptyState()
                        : _SessionList(videos: homeState.videos),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

// ── Sub-widgets ───────────────────────────────────────────────────────────────

class _HeroBanner extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ShaderMask(
          shaderCallback: (bounds) =>
              RerideColors.primaryGradient.createShader(bounds),
          child: const Text(
            'reride',
            style: TextStyle(
              fontSize: 64,
              fontWeight: FontWeight.w900,
              color: Colors.white,
              letterSpacing: 4,
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'Ride Smarter. Learn Faster.',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: RerideColors.accentLight,
                letterSpacing: 1.2,
              ),
        ),
      ],
    );
  }
}

class _UploadButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: RerideColors.primaryGradient,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: RerideColors.primary.withOpacity(0.4),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () => context.push(AppRoutes.upload),
          child: const Padding(
            padding: EdgeInsets.symmetric(vertical: 20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.cloud_upload_outlined,
                    size: 28, color: Colors.white),
                SizedBox(width: 12),
                Text(
                  'Upload Your Run',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                    letterSpacing: 0.5,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 48),
      child: Column(
        children: [
          Icon(Icons.snowboarding,
              size: 64,
              color: RerideColors.primaryLight.withOpacity(0.4)),
          const SizedBox(height: 16),
          Text(
            'No sessions yet',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: RerideColors.onSurface,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Upload your first run to get started!',
            style: Theme.of(context).textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  final String message;
  const _ErrorBanner({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: RerideColors.error.withOpacity(0.12),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: RerideColors.error.withOpacity(0.4)),
      ),
      child: Row(
        children: [
          const Icon(Icons.warning_amber_rounded,
              color: RerideColors.error, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                  color: RerideColors.error, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }
}

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
            const Icon(Icons.cloud_off_outlined,
                size: 64, color: RerideColors.error),
            const SizedBox(height: 16),
            Text(
              '연결 실패',
              style: Theme.of(context).textTheme.titleLarge,
            ),
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

/// Swipe-to-delete session list
class _SessionList extends ConsumerWidget {
  final List<VideoItem> videos;
  const _SessionList({required this.videos});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: videos.length,
      itemBuilder: (context, index) {
        final video = videos[index];
        return _SwipeableSessionCard(
          video: video,
          onDelete: () async {
            final confirmed = await _confirmDelete(context);
            if (confirmed) {
              await ref.read(homeProvider.notifier).delete(video.id);
            }
          },
        );
      },
    );
  }

  Future<bool> _confirmDelete(BuildContext context) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: RerideColors.surfaceCard,
        title: const Text('세션 삭제'),
        content: const Text('이 세션을 삭제할까요? 되돌릴 수 없습니다.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('취소'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(
                foregroundColor: RerideColors.error),
            child: const Text('삭제'),
          ),
        ],
      ),
    );
    return result ?? false;
  }
}

class _SwipeableSessionCard extends StatelessWidget {
  final VideoItem video;
  final VoidCallback onDelete;
  const _SwipeableSessionCard(
      {required this.video, required this.onDelete});

  String _formatDate(String createdAt) {
    try {
      final dt = DateTime.parse(createdAt).toLocal();
      return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')}';
    } catch (_) {
      return createdAt;
    }
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'done':
        return RerideColors.success;
      case 'processing':
        return RerideColors.accent;
      case 'failed':
        return RerideColors.error;
      default:
        return RerideColors.onSurface;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dismissible(
      key: Key(video.id),
      direction: DismissDirection.endToStart,
      background: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        decoration: BoxDecoration(
          color: RerideColors.error,
          borderRadius: BorderRadius.circular(16),
        ),
        child: const Icon(Icons.delete_outline,
            color: Colors.white, size: 28),
      ),
      confirmDismiss: (_) async {
        onDelete();
        return false; // We manage removal via provider
      },
      child: Card(
        child: ListTile(
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          leading: Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              gradient: RerideColors.primaryGradient,
              borderRadius: BorderRadius.circular(10),
            ),
            child: video.overallScore != null
                ? Center(
                    child: Text(
                      video.overallScore!.toStringAsFixed(0),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w800,
                        fontSize: 16,
                      ),
                    ),
                  )
                : const Icon(Icons.snowboarding, color: Colors.white),
          ),
          title: Text(
            'Session #${video.videoId}',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: RerideColors.onBackground,
                  fontWeight: FontWeight.w600,
                ),
          ),
          subtitle: Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: _statusColor(video.status).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  video.status.toUpperCase(),
                  style: TextStyle(
                    color: _statusColor(video.status),
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Text(
                _formatDate(video.createdAt),
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ],
          ),
          trailing: const Icon(Icons.chevron_right,
              color: RerideColors.primaryLight),
          onTap: () =>
              context.push(AppRoutes.analysisPath(video.id)),
        ),
      ),
    );
  }
}
