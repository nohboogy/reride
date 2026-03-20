import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:percent_indicator/percent_indicator.dart';
import 'package:video_player/video_player.dart';
import 'package:chewie/chewie.dart';
import '../../../core/constants/app_colors.dart';
import '../providers/analysis_provider.dart';
import '../../../services/api_service.dart';

class AnalysisResultScreen extends ConsumerStatefulWidget {
  final String analysisId;

  const AnalysisResultScreen({super.key, required this.analysisId});

  @override
  ConsumerState<AnalysisResultScreen> createState() =>
      _AnalysisResultScreenState();
}

class _AnalysisResultScreenState extends ConsumerState<AnalysisResultScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(analysisProvider.notifier).loadAnalysis(widget.analysisId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final analysisAsync = ref.watch(analysisProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('분석 결과'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => context.canPop() ? context.pop() : context.go('/'),
        ),
      ),
      body: analysisAsync.when(
        loading: () => const _LoadingView(),
        error: (err, _) => _ErrorView(message: err.toString()),
        data: (state) {
          if (state.isLoading) return const _LoadingView();
          if (state.isProcessing) {
            return _ProcessingView(
              progress: state.status?.progress,
              message: state.status?.message,
            );
          }
          if (state.isFailed) {
            return _ErrorView(message: state.error ?? '분석 실패');
          }
          if (state.isDone) {
            return _ResultView(result: state.result!);
          }
          return const _LoadingView();
        },
      ),
    );
  }
}

// ─────────────────────────────────────────
// 로딩 뷰
// ─────────────────────────────────────────

class _LoadingView extends StatelessWidget {
  const _LoadingView();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: CircularProgressIndicator(color: AppColors.primary),
    );
  }
}

// ─────────────────────────────────────────
// 처리 중 뷰 (폴링)
// ─────────────────────────────────────────

class _ProcessingView extends StatelessWidget {
  final int? progress;
  final String? message;

  const _ProcessingView({this.progress, this.message});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularPercentIndicator(
              radius: 70,
              lineWidth: 8,
              percent: (progress ?? 0) / 100.0,
              center: Text(
                '${progress ?? 0}%',
                style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                      color: AppColors.primary,
                      fontWeight: FontWeight.w700,
                    ),
              ),
              progressColor: AppColors.primary,
              backgroundColor: AppColors.surfaceVariant,
              animation: true,
              animateFromLastPercent: true,
            ),
            const SizedBox(height: 32),
            Text(
              'AI 분석 중...',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 12),
            Text(
              message ?? '포즈 추출 및 트릭 분류를 진행하고 있습니다',
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            // 단계 표시
            _buildStepIndicator(context, progress ?? 0),
          ],
        ),
      ),
    );
  }

  Widget _buildStepIndicator(BuildContext context, int progress) {
    final steps = [
      (label: '프레임 추출', threshold: 20),
      (label: '포즈 분석', threshold: 50),
      (label: '트릭 분류', threshold: 70),
      (label: '점수 산정', threshold: 85),
      (label: '애니메이션 생성', threshold: 95),
    ];

    return Column(
      children: steps.map((step) {
        final isDone = progress >= step.threshold;
        final isActive =
            progress >= (step.threshold - 20) && progress < step.threshold;
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                isDone
                    ? Icons.check_circle_rounded
                    : isActive
                        ? Icons.radio_button_checked_rounded
                        : Icons.radio_button_unchecked_rounded,
                color: isDone
                    ? AppColors.success
                    : isActive
                        ? AppColors.primary
                        : AppColors.textDisabled,
                size: 18,
              ),
              const SizedBox(width: 8),
              Text(
                step.label,
                style: TextStyle(
                  color: isDone
                      ? AppColors.textPrimary
                      : isActive
                          ? AppColors.primary
                          : AppColors.textDisabled,
                  fontSize: 13,
                  fontWeight:
                      isActive ? FontWeight.w600 : FontWeight.w400,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}

// ─────────────────────────────────────────
// 에러 뷰
// ─────────────────────────────────────────

class _ErrorView extends StatelessWidget {
  final String message;

  const _ErrorView({required this.message});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: AppColors.error, size: 64),
            const SizedBox(height: 16),
            Text(
              '분석 오류',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 8),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.go('/'),
              child: const Text('홈으로'),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────
// 결과 뷰
// ─────────────────────────────────────────

class _ResultView extends StatelessWidget {
  final AnalysisResult result;

  const _ResultView({required this.result});

  Color _getScoreColor(double score) {
    if (score >= 90) return AppColors.scoreExcellent;
    if (score >= 70) return AppColors.scoreGood;
    if (score >= 50) return AppColors.scoreAverage;
    return AppColors.scorePoor;
  }

  @override
  Widget build(BuildContext context) {
    final scoreColor = _getScoreColor(result.overallScore);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 종합 점수 카드
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  if (result.trickName != null) ...[
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        result.trickName!,
                        style: const TextStyle(
                          color: AppColors.primary,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],
                  CircularPercentIndicator(
                    radius: 70,
                    lineWidth: 10,
                    percent: result.overallScore / 100,
                    center: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          result.overallScore.toStringAsFixed(0),
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.w800,
                            color: scoreColor,
                          ),
                        ),
                        const Text(
                          '점',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                    progressColor: scoreColor,
                    backgroundColor: AppColors.surfaceVariant,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '종합 점수',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // 세부 점수
          if (result.detailedScores.isNotEmpty) ...[
            Text(
              '세부 분석',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: result.detailedScores.entries
                      .map((entry) => _ScoreRow(
                            label: entry.key,
                            score: entry.value,
                          ))
                      .toList(),
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // 피드백
          if (result.feedback.isNotEmpty) ...[
            Text(
              'AI 피드백',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: result.feedback
                      .asMap()
                      .entries
                      .map((entry) => Padding(
                            padding: const EdgeInsets.only(bottom: 10),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  width: 22,
                                  height: 22,
                                  decoration: BoxDecoration(
                                    color: AppColors.primary.withOpacity(0.2),
                                    shape: BoxShape.circle,
                                  ),
                                  child: Center(
                                    child: Text(
                                      '${entry.key + 1}',
                                      style: const TextStyle(
                                        color: AppColors.primary,
                                        fontSize: 11,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Text(
                                    entry.value,
                                    style:
                                        Theme.of(context).textTheme.bodyMedium,
                                  ),
                                ),
                              ],
                            ),
                          ))
                      .toList(),
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // 오버레이 영상
          if (result.overlayUrl != null) ...[
            Text(
              '오버레이 영상',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 12),
            _OverlayVideoPlayer(url: result.overlayUrl!),
            const SizedBox(height: 16),
          ],

          // 분석 날짜
          Text(
            '분석 일시: ${_formatDateTime(result.analyzedAt)}',
            style: Theme.of(context).textTheme.bodySmall,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),

          // 홈으로 버튼
          OutlinedButton(
            onPressed: () => context.canPop() ? context.pop() : context.go('/'),
            child: const Text('홈으로 돌아가기'),
          ),
        ],
      ),
    );
  }

  String _formatDateTime(DateTime dt) {
    return '${dt.year}.${dt.month.toString().padLeft(2, '0')}.${dt.day.toString().padLeft(2, '0')} '
        '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
}

class _ScoreRow extends StatelessWidget {
  final String label;
  final double score;

  const _ScoreRow({required this.label, required this.score});

  Color _color(double s) {
    if (s >= 90) return AppColors.scoreExcellent;
    if (s >= 70) return AppColors.scoreGood;
    if (s >= 50) return AppColors.scoreAverage;
    return AppColors.scorePoor;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: Theme.of(context).textTheme.bodyLarge),
              Text(
                score.toStringAsFixed(0),
                style: TextStyle(
                  color: _color(score),
                  fontWeight: FontWeight.w700,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          LinearPercentIndicator(
            lineHeight: 6,
            percent: score / 100,
            progressColor: _color(score),
            backgroundColor: AppColors.surfaceVariant,
            barRadius: const Radius.circular(3),
            padding: EdgeInsets.zero,
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────
// 오버레이 영상 플레이어
// ─────────────────────────────────────────

class _OverlayVideoPlayer extends StatefulWidget {
  final String url;

  const _OverlayVideoPlayer({required this.url});

  @override
  State<_OverlayVideoPlayer> createState() => _OverlayVideoPlayerState();
}

class _OverlayVideoPlayerState extends State<_OverlayVideoPlayer> {
  late VideoPlayerController _videoController;
  ChewieController? _chewieController;
  bool _initialized = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initPlayer();
  }

  Future<void> _initPlayer() async {
    try {
      _videoController = VideoPlayerController.networkUrl(
        Uri.parse(widget.url),
      );
      await _videoController.initialize();
      _chewieController = ChewieController(
        videoPlayerController: _videoController,
        aspectRatio: _videoController.value.aspectRatio,
        autoPlay: false,
        looping: false,
        allowFullScreen: true,
        allowMuting: true,
        placeholder: Container(color: AppColors.surfaceVariant),
      );
      if (mounted) setState(() => _initialized = true);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    }
  }

  @override
  void dispose() {
    _chewieController?.dispose();
    _videoController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return Container(
        height: 180,
        decoration: BoxDecoration(
          color: AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.videocam_off, color: AppColors.textDisabled, size: 36),
              SizedBox(height: 8),
              Text('영상을 불러올 수 없습니다',
                  style: TextStyle(color: AppColors.textDisabled, fontSize: 13)),
            ],
          ),
        ),
      );
    }

    if (!_initialized) {
      return Container(
        height: 180,
        decoration: BoxDecoration(
          color: AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(12),
        ),
        child: const Center(
          child: CircularProgressIndicator(color: AppColors.primary),
        ),
      );
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: AspectRatio(
        aspectRatio: _videoController.value.aspectRatio,
        child: Chewie(controller: _chewieController!),
      ),
    );
  }
}
