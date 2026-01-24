// import 'package:firebase_auth/firebase_auth.dart';  // Disabled - Firebase not in use
import '../../models/user_model.dart';
import '../../core/services/local_storage_service.dart';

class AuthResult {
  AuthResult({
    required this.success,
    this.message,
    this.user,
  });
  final bool success;
  final String? message;
  final UserModel? user;
}

class AuthService {
  // Mock auth service without Firebase
  // final FirebaseAuth _auth = FirebaseAuth.instance;

  // Current user stream
  Stream<UserModel?> get authStateChanges => Stream.value(null);

  // Current user
  UserModel? get currentUser => LocalStorageService.getUserData();

  // Check if user is logged in
  bool get isLoggedIn => LocalStorageService.getUserData() != null;

  // Sign up with email and password - Mock implementation
  Future<AuthResult> signUp({
    required String email,
    required String password,
    String? displayName,
  }) async {
    try {
      // Mock user creation
      final user = UserModel(
        uid: DateTime.now().millisecondsSinceEpoch.toString(),
        email: email,
        displayName: displayName,
        photoUrl: null,
        createdAt: DateTime.now(),
        lastLoginAt: DateTime.now(),
      );

      await LocalStorageService.saveUserData(user);
      await LocalStorageService.saveAuthToken('mock_token_${user.uid}');

      return AuthResult(
        success: true,
        message: 'Account created successfully (Mock)',
        user: user,
      );
    } catch (e) {
      return AuthResult(
        success: false,
        message: 'An unexpected error occurred',
      );
    }
  }

  // Sign in with email and password - Mock implementation
  Future<AuthResult> signIn({
    required String email,
    required String password,
  }) async {
    try {
      // Mock user login
      final user = UserModel(
        uid: DateTime.now().millisecondsSinceEpoch.toString(),
        email: email,
        displayName: email.split('@')[0],
        createdAt: DateTime.now(),
        lastLoginAt: DateTime.now(),
      );

      await LocalStorageService.saveUserData(user);
      await LocalStorageService.saveAuthToken('mock_token_${user.uid}');

      return AuthResult(
        success: true,
        message: 'Signed in successfully (Mock)',
        user: user,
      );
    } catch (e) {
      return AuthResult(
        success: false,
        message: 'An unexpected error occurred',
      );
    }
  }

  // Sign out - Mock implementation
  Future<AuthResult> signOut() async {
    try {
      await LocalStorageService.removeAuthToken();
      await LocalStorageService.removeUserData();

      return AuthResult(
        success: true,
        message: 'Signed out successfully',
      );
    } catch (e) {
      return AuthResult(
        success: false,
        message: 'Failed to sign out',
      );
    }
  }

  // Reset password - Mock implementation
  Future<AuthResult> resetPassword(String email) async {
    try {
      // Mock password reset - in real app, would send email
      return AuthResult(
        success: true,
        message: 'Password reset email sent (Mock)',
      );
    } catch (e) {
      return AuthResult(
        success: false,
        message: 'Failed to send password reset email',
      );
    }
  }

  // Refresh token - Mock implementation
  Future<String?> refreshToken() async {
    try {
      final user = LocalStorageService.getUserData();
      if (user != null) {
        final token = 'mock_token_${user.uid}_${DateTime.now().millisecondsSinceEpoch}';
        await LocalStorageService.saveAuthToken(token);
        return token;
      }
      return null;
    } catch (e) {
      return null;
    }
  }
}
