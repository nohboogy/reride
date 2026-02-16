import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants/api_constants.dart';
import '../../../services/api_service.dart';

class AnalysisState {
  final AnalysisResult? result;
  final AnalysisStatus? status;
  final bool isLoading;
  final String? error;
  final bool isPolling;

  const AnalysisState({
    this.result,
    this.status,
    this.isLoading = false,
    this.error,
    this.isPolling = false,
  });

  AnalysisState copyWith({
    AnalysisResult? result,
    AnalysisStatus? status,
    bool? isLoading,
    String? error,
    bool? isPolling,
  }) {
    return AnalysisState(
      result: result ?? this.result,
      status: status ?? this.status,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      isPolling: isPolling ?? this.isPolling,
    );
  }

  bool get isDone => result != null;
  bool get isFailed => error != null;
  bool get isProcessing => isPolling && result == null;
}

/// 분석 ID를 파라미터로 받는 family provider
class AnalysisNotifier extends AutoDisposeAsyncNotifier<AnalysisState> {
  Timer? _pollingTimer;
  String? _analysisId;

  @override
  Future<AnalysisState> build() async {
    ref.onDispose(() {
      _pollingTimer?.cancel();
    });
    return const AnalysisState();
  }

  Future<void> loadAnalysis(String analysisId) async {
    _analysisId = analysisId;
    state = const AsyncValue.data(AnalysisState(isLoading: true));

    try {
      final apiService = ref.read(apiServiceProvider);

      // 분석 상태 확인
      final status = await apiService.getAnalysisStatus(analysisId);
      state = AsyncValue.data(
        AnalysisState(status: status, isLoading: false),
      );

      if (status.status == 'done') {
        // 완료된 경우 결과 바로 로드
        final result = await apiService.getAnalysisResult(analysisId);
        state = AsyncValue.data(
          AnalysisState(result: result, status: status),
        );
      } else if (status.status == 'pending' ||
          status.status == 'processing') {
        // 아직 분석 중 → 폴링 시작
        _startPolling(analysisId);
      } else {
        // 실패
        state = AsyncValue.data(
          AnalysisState(
            status: status,
            error: '분석에 실패했습니다.',
          ),
        );
      }
    } catch (e) {
      state = AsyncValue.data(
        AnalysisState(error: e.toString()),
      );
    }
  }

  void _startPolling(String analysisId) {
    state = AsyncValue.data(
      AnalysisState(isPolling: true),
    );

    int retryCount = 0;

    _pollingTimer = Timer.periodic(
      Duration(milliseconds: ApiConstants.analysisPollingInterval),
      (timer) async {
        retryCount++;
        if (retryCount > ApiConstants.analysisMaxPollingRetries) {
          timer.cancel();
          state = const AsyncValue.data(
            AnalysisState(error: '분석 시간이 초과되었습니다.'),
          );
          return;
        }

        try {
          final apiService = ref.read(apiServiceProvider);
          final status = await apiService.getAnalysisStatus(analysisId);

          if (status.status == 'done') {
            timer.cancel();
            final result = await apiService.getAnalysisResult(analysisId);
            state = AsyncValue.data(
              AnalysisState(result: result, status: status),
            );
          } else if (status.status == 'failed') {
            timer.cancel();
            state = AsyncValue.data(
              AnalysisState(
                status: status,
                error: '분석에 실패했습니다.',
              ),
            );
          } else {
            state = AsyncValue.data(
              AnalysisState(status: status, isPolling: true),
            );
          }
        } catch (e) {
          // 폴링 중 에러는 무시하고 계속 시도
        }
      },
    );
  }
}

final analysisProvider =
    AutoDisposeAsyncNotifierProvider<AnalysisNotifier, AnalysisState>(
  AnalysisNotifier.new,
);
