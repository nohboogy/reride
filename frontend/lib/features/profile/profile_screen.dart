import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PROFILE'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
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
                'Rider',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              Text(
                'rider@reride.app',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 40),

              // ── Stats Row ────────────────────────────────────────────
              Row(
                children: [
                  _StatCard(label: 'Runs', value: '0'),
                  const SizedBox(width: 12),
                  _StatCard(label: 'Best Score', value: '—'),
                  const SizedBox(width: 12),
                  _StatCard(label: 'Streak', value: '0 days'),
                ],
              ),
              const SizedBox(height: 32),

              // ── Settings List ────────────────────────────────────────
              _SettingsItem(
                icon: Icons.notifications_outlined,
                label: 'Notifications',
                onTap: () {},
              ),
              _SettingsItem(
                icon: Icons.language_outlined,
                label: 'Language',
                onTap: () {},
              ),
              _SettingsItem(
                icon: Icons.help_outline,
                label: 'Help & Feedback',
                onTap: () {},
              ),
              _SettingsItem(
                icon: Icons.logout,
                label: 'Sign Out',
                destructive: true,
                onTap: () {
                  context.go('/');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

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
    final color = destructive ? RerideColors.error : RerideColors.onBackground;
    return ListTile(
      leading: Icon(icon, color: color),
      title: Text(label, style: TextStyle(color: color, fontWeight: FontWeight.w500)),
      trailing: destructive
          ? null
          : const Icon(Icons.chevron_right, color: RerideColors.primaryLight),
      onTap: onTap,
    );
  }
}
