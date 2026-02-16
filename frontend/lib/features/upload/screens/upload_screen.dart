import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../../../core/constants/app_colors.dart';
import '../providers/upload_provider.dart';

class UploadScreen extends ConsumerWidget {
  const UploadScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final uploadState = ref.watch(uploadProvider);

    // 업로드 완료 시 분석 결과 화면으로 이동
    ref.listen(uploadProvider, (previous, next) {
      if (next.isDone && next.uploadedVideo?.id.isNotEmpty == true) {
        context.go('/analysis/${next.uploadedVideo!.id}');
        ref.read(uploadProvider.notifier).reset();
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('영상 업로드'),
        leading: IconButton(
          icon: const Icon(Icons.close_rounded),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 안내 텍스트
              Text(
                '스노보드 영상을 업로드하세요',
                style: Theme.of(context).textTheme.headlineMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'AI가 자세를 분석하고 트릭을 인식합니다.\n최대 5분, 파일 크기 500MB 이하',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 32),

              // 영상 선택 영역
              Expanded(
                child: _buildPickerArea(context, ref, uploadState),
              ),

              const SizedBox(height: 20),

              // 업로드 버튼
              if (uploadState.selectedFile != null &&
                  !uploadState.isUploading &&
                  !uploadState.isDone)
                ElevatedButton.icon(
                  onPressed: () =>
                      ref.read(uploadProvider.notifier).uploadVideo(),
                  icon: const Icon(Icons.cloud_upload_rounded),
                  label: const Text('분석 시작'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.all(16),
                  ),
                ),

              if (uploadState.hasError)
                Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.error.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: AppColors.error.withOpacity(0.3),
                      ),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline,
                            color: AppColors.error, size: 18),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            uploadState.error ?? '업로드 실패',
                            style: const TextStyle(
                              color: AppColors.error,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPickerArea(
    BuildContext context,
    WidgetRef ref,
    UploadState uploadState,
  ) {
    if (uploadState.isUploading) {
      return _buildUploadingState(context, uploadState);
    }

    if (uploadState.selectedFile != null) {
      return _buildSelectedState(context, ref, uploadState);
    }

    return _buildInitialState(context, ref);
  }

  Widget _buildInitialState(BuildContext context, WidgetRef ref) {
    return GestureDetector(
      onTap: () => _pickVideo(ref),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: AppColors.primary.withOpacity(0.3),
            width: 2,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: AppColors.primary.withOpacity(0.15),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.video_library_rounded,
                color: AppColors.primary,
                size: 40,
              ),
            ),
            const SizedBox(height: 20),
            Text(
              '영상 선택',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              '탭하여 갤러리에서 영상을 선택하세요',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              children: ['MP4', 'MOV', 'AVI']
                  .map((ext) => Chip(
                        label: Text(ext),
                        backgroundColor: AppColors.surface,
                        side: BorderSide.none,
                        labelStyle: const TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 11,
                        ),
                      ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSelectedState(
    BuildContext context,
    WidgetRef ref,
    UploadState state,
  ) {
    final file = state.selectedFile!;
    final fileName = file.path.split('/').last;
    final fileSize = file.lengthSync();
    final fileSizeMB = fileSize / (1024 * 1024);

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: AppColors.primary,
          width: 2,
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.check_circle_rounded,
              color: AppColors.primary,
              size: 40,
            ),
          ),
          const SizedBox(height: 20),
          Text(
            '영상 선택 완료',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            fileName,
            style: Theme.of(context).textTheme.bodyMedium,
            maxLines: 2,
            textAlign: TextAlign.center,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            '${fileSizeMB.toStringAsFixed(1)} MB',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 16),
          TextButton.icon(
            onPressed: () => _pickVideo(ref),
            icon: const Icon(Icons.change_circle_outlined, size: 18),
            label: const Text('다른 영상 선택'),
          ),
        ],
      ),
    );
  }

  Widget _buildUploadingState(BuildContext context, UploadState state) {
    final percent = (state.uploadProgress * 100).toInt();

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 100,
                height: 100,
                child: CircularProgressIndicator(
                  value: state.uploadProgress,
                  strokeWidth: 6,
                  backgroundColor: AppColors.surface,
                  color: AppColors.primary,
                ),
              ),
              Text(
                '$percent%',
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      color: AppColors.primary,
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            '업로드 중...',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 8),
          Text(
            'AI 분석을 위해 영상을 전송하고 있습니다',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }

  Future<void> _pickVideo(WidgetRef ref) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickVideo(
      source: ImageSource.gallery,
      maxDuration: const Duration(minutes: 5),
    );

    if (pickedFile != null) {
      ref.read(uploadProvider.notifier).selectFile(File(pickedFile.path));
    }
  }
}
