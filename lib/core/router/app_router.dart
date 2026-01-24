import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/auth_provider.dart';
import '../../auth/screens/login_screen.dart';
import '../../auth/screens/signup_screen.dart';
import '../../auth/screens/forgot_password_screen.dart';
import '../../screens/main_screen.dart';
import '../../screens/alerts/alerts_screen.dart';
import '../../screens/alerts/alert_detail_screen.dart';
import '../../screens/gallery/gallery_screen.dart';
import '../../screens/gallery/snapshot_preview_screen.dart';
import '../../screens/profile/profile_screen.dart';
import '../../screens/splash_screen.dart';

// Route names
class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String signup = '/signup';
  static const String forgotPassword = '/forgot-password';
  static const String main = '/main';
  static const String alerts = '/alerts';
  static const String alertDetail = '/alert-detail';
  static const String gallery = '/gallery';
  static const String snapshotPreview = '/snapshot-preview';
  static const String profile = '/profile';
}

// Router Configuration
final appRouterProvider = Provider<RouterConfig<Object>>((ref) {
  return MaterialRouter(ref);
});

class MaterialRouter extends RouterConfig<Object> {
  MaterialRouter(this.ref)
      : super(
          routerDelegate: _createRouterDelegate(ref),
          routeInformationParser: _RouteInformationParser(),
          routeInformationProvider: PlatformRouteInformationProvider(
            initialRouteInformation: RouteInformation(
              uri: Uri.parse(AppRoutes.splash),
            ),
          ),
        );

  final Ref ref;

  static RouterDelegate<Object> _createRouterDelegate(Ref ref) {
    return _AppRouterDelegate(ref);
  }
}

class _RouteInformationParser extends RouteInformationParser<String> {
  @override
  Future<String> parseRouteInformation(
      RouteInformation routeInformation) async {
    return routeInformation.uri.path;
  }

  @override
  RouteInformation? restoreRouteInformation(String configuration) {
    return RouteInformation(uri: Uri.parse(configuration));
  }
}

class _AppRouterDelegate extends RouterDelegate<String>
    with ChangeNotifier, PopNavigatorRouterDelegateMixin<String> {
  _AppRouterDelegate(this.ref);

  final Ref ref;

  @override
  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

  String _currentPath = AppRoutes.splash;
  Object? _arguments;

  @override
  String get currentConfiguration => _currentPath;

  void navigate(String path, {Object? arguments}) {
    _currentPath = path;
    _arguments = arguments;
    notifyListeners();
  }

  void pop() {
    if (_currentPath != AppRoutes.splash &&
        _currentPath != AppRoutes.login &&
        _currentPath != AppRoutes.main) {
      navigatorKey.currentState?.pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Navigator(
      key: navigatorKey,
      pages: _buildPages(),
      onPopPage: (route, result) {
        if (!route.didPop(result)) {
          return false;
        }
        return true;
      },
    );
  }

  List<Page<dynamic>> _buildPages() {
    final pages = <Page<dynamic>>[];

    // Always show splash first
    pages.add(
      MaterialPage(
        key: const ValueKey('splash'),
        child: SplashScreen(
          onInitialized: (isLoggedIn) {
            if (isLoggedIn) {
              navigate(AppRoutes.main);
            } else {
              navigate(AppRoutes.login);
            }
          },
        ),
      ),
    );

    if (_currentPath == AppRoutes.login) {
      pages.add(
        MaterialPage(
          key: const ValueKey('login'),
          child: LoginScreen(
            onLoginSuccess: () => navigate(AppRoutes.main),
            onSignUpTap: () => navigate(AppRoutes.signup),
            onForgotPasswordTap: () => navigate(AppRoutes.forgotPassword),
          ),
        ),
      );
    }

    if (_currentPath == AppRoutes.signup) {
      pages.add(
        MaterialPage(
          key: const ValueKey('signup'),
          child: SignUpScreen(
            onSignUpSuccess: () => navigate(AppRoutes.main),
            onLoginTap: () => navigate(AppRoutes.login),
          ),
        ),
      );
    }

    if (_currentPath == AppRoutes.forgotPassword) {
      pages.add(
        MaterialPage(
          key: const ValueKey('forgot_password'),
          child: ForgotPasswordScreen(
            onBackToLogin: () => navigate(AppRoutes.login),
          ),
        ),
      );
    }

    if (_currentPath == AppRoutes.main) {
      pages.add(
        MaterialPage(
          key: const ValueKey('main'),
          child: MainScreen(
            onLogout: () => navigate(AppRoutes.login),
          ),
        ),
      );
    }

    if (_currentPath == AppRoutes.alertDetail) {
      final alertId = _arguments as String?;
      pages.add(
        MaterialPage(
          key: ValueKey('alert_detail_$alertId'),
          child: AlertDetailScreen(alertId: alertId ?? ''),
        ),
      );
    }

    if (_currentPath == AppRoutes.snapshotPreview) {
      final args = _arguments as Map<String, dynamic>?;
      pages.add(
        MaterialPage(
          key: const ValueKey('snapshot_preview'),
          child: SnapshotPreviewScreen(
            imageUrl: args?['imageUrl'] ?? '',
            timestamp: args?['timestamp'] ?? DateTime.now(),
          ),
        ),
      );
    }

    return pages;
  }

  @override
  Future<void> setNewRoutePath(String configuration) async {
    _currentPath = configuration;
    notifyListeners();
  }
}

// Navigation helper
final navigationProvider = Provider<AppNavigation>((ref) {
  final router = ref.watch(appRouterProvider);
  return AppNavigation(router.routerDelegate as _AppRouterDelegate);
});

class AppNavigation {
  AppNavigation(this._delegate);
  final _AppRouterDelegate _delegate;

  void navigateTo(String route, {Object? arguments}) {
    _delegate.navigate(route, arguments: arguments);
  }

  void goBack() {
    _delegate.pop();
  }

  void navigateToLogin() => navigateTo(AppRoutes.login);
  void navigateToSignUp() => navigateTo(AppRoutes.signup);
  void navigateToMain() => navigateTo(AppRoutes.main);
  void navigateToAlertDetail(String alertId) =>
      navigateTo(AppRoutes.alertDetail, arguments: alertId);
  void navigateToSnapshotPreview(String imageUrl, DateTime timestamp) =>
      navigateTo(
        AppRoutes.snapshotPreview,
        arguments: {
          'imageUrl': imageUrl,
          'timestamp': timestamp,
        },
      );
}
