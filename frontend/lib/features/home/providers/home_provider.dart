import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../services/api_service.dart';

/// 홈 화면의 비디오 목록 상태
class HomeState {
  final List<VideoItem> videos;
  final bool isLoading;
  final String? error;

  const HomeState({
    this.videos = const [],
    this.isLoading = false,
    this.error,
  });

  HomeState copyWith({
    List<VideoItem>? videos,
    bool? isLoading,
    String? error,
  }) {
    return HomeState(
      videos: videos ?? this.videos,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// 홈 화면 Notifier
class HomeNotifier extends AsyncNotifier<HomeState> {
  @override
  Future<HomeState> build() async {
    return _fetchVideos();
  }

  Future<HomeState> _fetchVideos() async {
    final apiService = ref.read(apiServiceProvider);
    try {
      final videos = await apiService.listAnalyses();
      return HomeState(videos: videos);
    } catch (e) {
      return HomeState(error: e.toString());
    }
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _fetchVideos());
  }

  /// Delete an analysis by ID, then remove it from the local list.
  Future<void> delete(String analysisId) async {
    final current = state.value;
    if (current == null) return;
    try {
      final apiService = ref.read(apiServiceProvider);
      await apiService.deleteAnalysis(analysisId);
      final updated = current.videos
          .where((v) => v.id != analysisId)
          .toList();
      state = AsyncValue.data(current.copyWith(videos: updated));
    } catch (e) {
      // Keep existing list; surface error
      state = AsyncValue.data(current.copyWith(error: e.toString()));
    }
  }
}

final homeProvider = AsyncNotifierProvider<HomeNotifier, HomeState>(
  HomeNotifier.new,
);
