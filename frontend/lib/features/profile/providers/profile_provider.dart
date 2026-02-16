import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../services/api_service.dart';

// UserProfile is just the raw map returned by the API
typedef UserProfile = Map<String, dynamic>;

class ProfileState {
  final UserProfile? profile;
  final bool isLoading;
  final String? error;

  const ProfileState({
    this.profile,
    this.isLoading = false,
    this.error,
  });

  ProfileState copyWith({
    UserProfile? profile,
    bool? isLoading,
    String? error,
  }) {
    return ProfileState(
      profile: profile ?? this.profile,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class ProfileNotifier extends AsyncNotifier<ProfileState> {
  @override
  Future<ProfileState> build() async {
    return _fetchProfile();
  }

  Future<ProfileState> _fetchProfile() async {
    try {
      final apiService = ref.read(apiServiceProvider);
      final profile = await apiService.getProfile();
      return ProfileState(profile: profile);
    } catch (e) {
      return ProfileState(error: e.toString());
    }
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _fetchProfile());
  }

  Future<void> updateProfile(Map<String, dynamic> data) async {
    final current = state.value;
    state = const AsyncLoading();
    try {
      final apiService = ref.read(apiServiceProvider);
      final updated = await apiService.updateProfile(data);
      state = AsyncValue.data(ProfileState(profile: updated));
    } catch (e) {
      state = AsyncValue.data(
        ProfileState(
          profile: current?.profile,
          error: e.toString(),
        ),
      );
    }
  }
}

final profileProvider =
    AsyncNotifierProvider<ProfileNotifier, ProfileState>(ProfileNotifier.new);
