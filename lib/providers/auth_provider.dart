// import 'package:firebase_auth/firebase_auth.dart';  // Disabled - Firebase not in use
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/services/auth_service.dart';
import '../core/services/local_storage_service.dart';
import '../models/user_model.dart';

// Auth Service Provider
final authServiceProvider = Provider<AuthService>((ref) => AuthService());

// Auth State Provider
final authStateProvider = StreamProvider<UserModel?>((ref) {
  final authService = ref.watch(authServiceProvider);
  return authService.authStateChanges;
});

// Current User Provider
final currentUserProvider = Provider<UserModel?>((ref) {
  final authState = ref.watch(authStateProvider);
  return authState.valueOrNull;
});

// Is Logged In Provider
final isLoggedInProvider = Provider<bool>((ref) {
  final user = ref.watch(currentUserProvider);
  return user != null;
});

// User Model Provider
final userModelProvider =
    StateNotifierProvider<UserModelNotifier, UserModel?>((ref) {
  return UserModelNotifier();
});

class UserModelNotifier extends StateNotifier<UserModel?> {
  UserModelNotifier() : super(null) {
    _loadUserFromStorage();
  }

  void _loadUserFromStorage() {
    state = LocalStorageService.getUserData();
  }

  void setUser(UserModel? user) {
    state = user;
    if (user != null) {
      LocalStorageService.saveUserData(user);
    } else {
      LocalStorageService.removeUserData();
    }
  }

  void clearUser() {
    state = null;
    LocalStorageService.removeUserData();
  }
}

// Auth Loading Provider
final authLoadingProvider = StateProvider<bool>((ref) => false);

// Auth Error Provider
final authErrorProvider = StateProvider<String?>((ref) => null);
