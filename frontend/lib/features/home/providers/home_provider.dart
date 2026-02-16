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
}

final homeProvider = AsyncNotifierProvider<HomeNotifier, HomeState>(
  HomeNotifier.new,
);
