import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../../services/api_service.dart';

enum UploadStatus { idle, picking, uploading, done, error }

class UploadState {
  final UploadStatus status;
  final XFile? selectedFile;       // XFile works on web + mobile
  final double uploadProgress;     // 0.0 ~ 1.0
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
    XFile? selectedFile,
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

  void selectFile(XFile file) {
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
      final xFile = state.selectedFile!;
      // 웹에서는 파일 바이트를 먼저 읽어야 함 (MultipartFile.fromFile 미지원)
      final bytes = await xFile.readAsBytes();
      final video = await apiService.uploadVideo(
        filePath: xFile.path,
        fileName: xFile.name,
        fileBytes: bytes,
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
