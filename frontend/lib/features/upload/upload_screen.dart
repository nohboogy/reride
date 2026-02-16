import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme.dart';

class UploadScreen extends StatelessWidget {
  const UploadScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('UPLOAD RUN'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 16),

              // ── Drop Zone ────────────────────────────────────────────
              _DropZone(),
              const SizedBox(height: 32),

              // ── Video Info Form (placeholder) ────────────────────────
              _VideoInfoSection(),
              const Spacer(),

              // ── Submit Button ────────────────────────────────────────
              _SubmitButton(),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}

class _DropZone extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        // TODO: open image_picker for video
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Video picker coming soon!')),
        );
      },
      child: Container(
        height: 220,
        decoration: BoxDecoration(
          color: RerideColors.surfaceCard,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: RerideColors.primary.withOpacity(0.5),
            width: 2,
            // dashed look via container — real dashed border can use DashedBorder package
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ShaderMask(
              shaderCallback: (bounds) =>
                  RerideColors.primaryGradient.createShader(bounds),
              child: const Icon(
                Icons.cloud_upload_outlined,
                size: 72,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Tap to select your video',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: RerideColors.onBackground,
                    fontWeight: FontWeight.w600,
                  ),
            ),
            const SizedBox(height: 6),
            Text(
              'MP4, MOV • up to 500 MB',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }
}

class _VideoInfoSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Session Details',
            style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 16),
        TextField(
          decoration: const InputDecoration(
            labelText: 'Title',
            hintText: 'e.g. Morning run at Hakuba',
            prefixIcon: Icon(Icons.edit_outlined),
          ),
        ),
        const SizedBox(height: 12),
        TextField(
          decoration: const InputDecoration(
            labelText: 'Resort / Location',
            hintText: 'e.g. Hakuba Valley',
            prefixIcon: Icon(Icons.location_on_outlined),
          ),
        ),
      ],
    );
  }
}

class _SubmitButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      decoration: BoxDecoration(
        gradient: RerideColors.primaryGradient,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: RerideColors.primary.withOpacity(0.4),
            blurRadius: 16,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(14),
          onTap: () {
            // TODO: call ApiService.uploadVideo()
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Upload feature coming soon!')),
            );
          },
          child: const Center(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.rocket_launch_outlined,
                    color: Colors.white, size: 22),
                SizedBox(width: 10),
                Text(
                  'Analyse My Run',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 17,
                    fontWeight: FontWeight.w700,
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
