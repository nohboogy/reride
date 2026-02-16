import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme.dart';

class AnalysisScreen extends StatelessWidget {
  final String analysisId;

  const AnalysisScreen({super.key, required this.analysisId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('ANALYSIS'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.share_outlined),
            tooltip: 'Share',
            onPressed: () {
              // TODO: share_plus integration
            },
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // ── ID chip ──────────────────────────────────────────────
              _IdChip(analysisId: analysisId),
              const SizedBox(height: 24),

              // ── Score Card ───────────────────────────────────────────
              _ScoreCard(),
              const SizedBox(height: 24),

              // ── Breakdown Metrics ────────────────────────────────────
              Text('Breakdown',
                  style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 12),
              _MetricsList(),
              const SizedBox(height: 24),

              // ── AI Feedback ──────────────────────────────────────────
              Text('AI Coach Feedback',
                  style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 12),
              _FeedbackCard(),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Sub-widgets ──────────────────────────────────────────────────────────────

class _IdChip extends StatelessWidget {
  final String analysisId;
  const _IdChip({required this.analysisId});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: RerideColors.surfaceCard,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: RerideColors.divider),
      ),
      child: Text(
        'ID: $analysisId',
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontFamily: 'monospace',
              color: RerideColors.accentLight,
            ),
      ),
    );
  }
}

class _ScoreCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: RerideColors.primaryGradient,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: RerideColors.primary.withOpacity(0.35),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          const Text(
            'Overall Score',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 14,
              fontWeight: FontWeight.w500,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            '—',
            style: TextStyle(
              color: Colors.white,
              fontSize: 56,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Pending analysis…',
            style: TextStyle(
              color: Colors.white.withOpacity(0.7),
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricsList extends StatelessWidget {
  static const _metrics = [
    ('Balance', Icons.balance_outlined, '—'),
    ('Edge Control', Icons.settings_outlined, '—'),
    ('Speed', Icons.speed_outlined, '—'),
    ('Carve Quality', Icons.gesture_outlined, '—'),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      children: _metrics.map((m) {
        final (label, icon, value) = m;
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: RerideColors.surfaceElevated,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: RerideColors.primaryLight, size: 20),
            ),
            title: Text(
              label,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: RerideColors.onBackground,
                  ),
            ),
            trailing: Text(
              value,
              style: const TextStyle(
                color: RerideColors.primaryLight,
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}

class _FeedbackCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: RerideColors.surfaceCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: RerideColors.divider),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              gradient: RerideColors.primaryGradient,
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.smart_toy_outlined,
                color: Colors.white, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Analysis pending — upload a video to receive personalised feedback from your AI coach.',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: RerideColors.onSurface,
                    height: 1.6,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}
