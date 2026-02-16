import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/router.dart';
import '../../core/theme.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('RERIDE'),
        actions: [
          IconButton(
            icon: const Icon(Icons.person_outline),
            tooltip: 'Profile',
            onPressed: () => context.go(AppRoutes.profile),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // ── Hero Logo / Tagline ──────────────────────────────────
              _HeroBanner(),
              const SizedBox(height: 40),

              // ── Upload CTA ───────────────────────────────────────────
              _UploadButton(),
              const SizedBox(height: 40),

              // ── Recent Analyses (placeholder) ────────────────────────
              Align(
                alignment: Alignment.centerLeft,
                child: Text('Recent Sessions', style: textTheme.titleLarge),
              ),
              const SizedBox(height: 16),
              _RecentSessionsList(),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Sub-widgets ──────────────────────────────────────────────────────────────

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
          onTap: () => context.go(AppRoutes.upload),
          child: const Padding(
            padding: EdgeInsets.symmetric(vertical: 20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.cloud_upload_outlined, size: 28, color: Colors.white),
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

class _RecentSessionsList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Placeholder — will be replaced with Riverpod provider + API data
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: 3,
      itemBuilder: (context, index) {
        return Card(
          child: ListTile(
            leading: Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                gradient: RerideColors.primaryGradient,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.snowboarding, color: Colors.white),
            ),
            title: Text(
              'Run #${index + 1}',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: RerideColors.onBackground,
                    fontWeight: FontWeight.w600,
                  ),
            ),
            subtitle: Text(
              'Tap to view analysis',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            trailing: const Icon(
              Icons.chevron_right,
              color: RerideColors.primaryLight,
            ),
            onTap: () => context.go(AppRoutes.analysisPath('demo-$index')),
          ),
        );
      },
    );
  }
}
