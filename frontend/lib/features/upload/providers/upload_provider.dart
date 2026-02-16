import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../services/api_service.dart';

enum UploadStatus { idle, picking, uploading, done, error }

class UploadState {
  final UploadStatus status;
  final File? selectedFile;
  final double uploadProgress; // 0.0 ~ 1.0
  final String? error;
  final VideoItem? uploadedVideo;

  const UploadState({
    this.status = UploadStatus.idle,
    this.selectedFile,
    this.uploadProgress = 0.0,
    this.error,
    this.uploadedVideo,
  });

  UploadState copyWith({
    UploadStatus? status,
    File? selectedFile,
    double? uploadProgress,
    String? error,
    VideoItem? uploadedVideo,
  }) {
    return UploadState(
      status: status ?? this.status,
      selectedFile: selectedFile ?? this.selectedFile,
      uploadProgress: uploadProgress ?? this.uploadProgress,
      error: error,
      uploadedVideo: uploadedVideo ?? this.uploadedVideo,
    );
  }

  bool get isUploading => status == UploadStatus.uploading;
  bool get isDone => status == UploadStatus.done;
  bool get hasError => status == UploadStatus.error;
}

class UploadNotifier extends Notifier<UploadState> {
  @override
  UploadState build() => const UploadState();

  void selectFile(File file) {
    state = state.copyWith(
      status: UploadStatus.picking,
      selectedFile: file,
    );
  }

  Future<void> uploadVideo() async {
    if (state.selectedFile == null) return;

    state = state.copyWith(
      status: UploadStatus.uploading,
      uploadProgress: 0.0,
    );

    try {
      final apiService = ref.read(apiServiceProvider);
      final video = await apiService.uploadVideo(
        filePath: state.selectedFile!.path,
        onSendProgress: (sent, total) {
          final progress = total > 0 ? sent / total : 0.0;
          state = state.copyWith(uploadProgress: progress);
        },
      );

      state = state.copyWith(
        status: UploadStatus.done,
        uploadedVideo: video,
      );
    } catch (e) {
      state = state.copyWith(
        status: UploadStatus.error,
        error: e.toString(),
      );
    }
  }

  void reset() {
    state = const UploadState();
  }
}

final uploadProvider = NotifierProvider<UploadNotifier, UploadState>(
  UploadNotifier.new,
);
