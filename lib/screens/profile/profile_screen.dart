import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/auth_provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/camera_provider.dart';
import '../../core/theme/app_colors.dart';
import '../cameras/cameras_screen.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key, required this.onLogout});
  final VoidCallback onLogout;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final user = ref.watch(userModelProvider);
    final currentUser = ref.watch(currentUserProvider);
    final themeMode = ref.watch(themeModeProvider);
    final cameraStatus = ref.watch(cameraStatusProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Profile Header
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: AppColors.primaryGradient,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withValues(alpha: 0.3),
                    blurRadius: 15,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: Column(
                children: [
                  // Avatar
                  Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.2),
                      shape: BoxShape.circle,
                    ),
                    child: currentUser?.photoUrl != null
                        ? ClipOval(
                            child: Image.network(
                              currentUser!.photoUrl!,
                              fit: BoxFit.cover,
                            ),
                          )
                        : const Icon(
                            Icons.person,
                            size: 40,
                            color: Colors.white,
                          ),
                  ),
                  const SizedBox(height: 16),
                  // Name
                  Text(
                    user?.displayName ?? currentUser?.displayName ?? 'User',
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 4),
                  // Email
                  Text(
                    user?.email ?? currentUser?.email ?? 'No email',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withValues(alpha: 0.8),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // System Status Card
            _buildCard(
              context,
              isDark,
              title: 'System Status',
              icon: Icons.monitor_heart_outlined,
              children: [
                _buildStatusItem(
                  context,
                  icon: Icons.videocam,
                  label: 'Camera',
                  value: cameraStatus.statusLabel,
                  valueColor: cameraStatus.isOnline
                      ? AppColors.success
                      : AppColors.error,
                  isDark: isDark,
                ),
                const Divider(height: 24),
                _buildStatusItem(
                  context,
                  icon: Icons.shield_outlined,
                  label: 'Detection',
                  value: 'Active',
                  valueColor: AppColors.success,
                  isDark: isDark,
                ),
                const Divider(height: 24),
                _buildStatusItem(
                  context,
                  icon: Icons.notifications_active_outlined,
                  label: 'Notifications',
                  value: 'Enabled',
                  valueColor: AppColors.success,
                  isDark: isDark,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Settings Card
            _buildCard(
              context,
              isDark,
              title: 'Settings',
              icon: Icons.settings_outlined,
              children: [
                _buildSettingItem(
                  context,
                  icon: Icons.dark_mode_outlined,
                  label: 'Dark Mode',
                  trailing: Switch.adaptive(
                    value: themeMode == ThemeMode.dark,
                    onChanged: (value) {
                      ref.read(themeModeProvider.notifier).setThemeMode(
                            value ? ThemeMode.dark : ThemeMode.light,
                          );
                    },
                    activeColor: AppColors.primary,
                  ),
                  isDark: isDark,
                ),
                const Divider(height: 24),
                _buildSettingItem(
                  context,
                  icon: Icons.notifications_outlined,
                  label: 'Push Notifications',
                  trailing: Switch.adaptive(
                    value: true,
                    onChanged: (value) {
                      // TODO: Toggle notifications
                    },
                    activeColor: AppColors.primary,
                  ),
                  isDark: isDark,
                ),
                const Divider(height: 24),
                _buildSettingItem(
                  context,
                  icon: Icons.volume_up_outlined,
                  label: 'Alarm Sound',
                  trailing: Switch.adaptive(
                    value: true,
                    onChanged: (value) {
                      // TODO: Toggle alarm sound
                    },
                    activeColor: AppColors.primary,
                  ),
                  isDark: isDark,
                ),
                const Divider(height: 24),
                _buildSettingItem(
                  context,
                  icon: Icons.vibration,
                  label: 'Vibration',
                  trailing: Switch.adaptive(
                    value: true,
                    onChanged: (value) {
                      // TODO: Toggle vibration
                    },
                    activeColor: AppColors.primary,
                  ),
                  isDark: isDark,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Camera Settings Card
            _buildCard(
              context,
              isDark,
              title: 'Camera Settings',
              icon: Icons.videocam_outlined,
              children: [
                _buildSettingItem(
                  context,
                  icon: Icons.video_settings,
                  label: 'Manage Cameras',
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const CamerasScreen(),
                      ),
                    );
                  },
                  isDark: isDark,
                ),
                const Divider(height: 24),
                _buildSettingItem(
                  context,
                  icon: Icons.timer_outlined,
                  label: 'Refresh Interval',
                  value: '3 seconds',
                  onTap: () => _showRefreshIntervalPicker(context),
                  isDark: isDark,
                ),
                const Divider(height: 24),
                _buildSettingItem(
                  context,
                  icon: Icons.wifi_outlined,
                  label: 'Server Address',
                  value: '192.168.1.100',
                  onTap: () => _showServerSettings(context),
                  isDark: isDark,
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Support Card
            _buildCard(
              context,
              isDark,
              title: 'Support',
              icon: Icons.help_outline,
              children: [
                _buildSettingItem(
                  context,
                  icon: Icons.info_outline,
                  label: 'About',
                  onTap: () => _showAboutDialog(context),
                  isDark: isDark,
                ),
                const Divider(height: 24),
                _buildSettingItem(
                  context,
                  icon: Icons.privacy_tip_outlined,
                  label: 'Privacy Policy',
                  onTap: () {
                    // TODO: Open privacy policy
                  },
                  isDark: isDark,
                ),
                const Divider(height: 24),
                _buildSettingItem(
                  context,
                  icon: Icons.description_outlined,
                  label: 'Terms of Service',
                  onTap: () {
                    // TODO: Open terms of service
                  },
                  isDark: isDark,
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Logout Button
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () => _showLogoutConfirmation(context, ref),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.error,
                  side: const BorderSide(color: AppColors.error),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                icon: const Icon(Icons.logout),
                label: const Text(
                  'Sign Out',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // App Version
            Text(
              'Alertix v1.0.0',
              style: TextStyle(
                fontSize: 12,
                color: isDark
                    ? AppColors.textSecondaryDark
                    : AppColors.textSecondaryLight,
              ),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildCard(
    BuildContext context,
    bool isDark, {
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? AppColors.cardDark : AppColors.cardLight,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                icon,
                size: 20,
                color: isDark ? AppColors.primaryDark : AppColors.primary,
              ),
              const SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: isDark ? Colors.white : AppColors.textPrimaryLight,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...children,
        ],
      ),
    );
  }

  Widget _buildStatusItem(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
    required Color valueColor,
    required bool isDark,
  }) {
    return Row(
      children: [
        Icon(
          icon,
          size: 20,
          color: isDark
              ? AppColors.textSecondaryDark
              : AppColors.textSecondaryLight,
        ),
        const SizedBox(width: 12),
        Text(
          label,
          style: TextStyle(
            fontSize: 14,
            color:
                isDark ? AppColors.textPrimaryDark : AppColors.textPrimaryLight,
          ),
        ),
        const Spacer(),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: valueColor.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            value,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: valueColor,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSettingItem(
    BuildContext context, {
    required IconData icon,
    required String label,
    required bool isDark,
    String? value,
    Widget? trailing,
    VoidCallback? onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Row(
        children: [
          Icon(
            icon,
            size: 20,
            color: isDark
                ? AppColors.textSecondaryDark
                : AppColors.textSecondaryLight,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 14,
                color: isDark
                    ? AppColors.textPrimaryDark
                    : AppColors.textPrimaryLight,
              ),
            ),
          ),
          if (value != null)
            Text(
              value,
              style: TextStyle(
                fontSize: 14,
                color: isDark
                    ? AppColors.textSecondaryDark
                    : AppColors.textSecondaryLight,
              ),
            ),
          if (trailing != null) trailing,
          if (onTap != null && trailing == null)
            Icon(
              Icons.chevron_right,
              color: isDark
                  ? AppColors.textSecondaryDark
                  : AppColors.textSecondaryLight,
            ),
        ],
      ),
    );
  }

  void _showRefreshIntervalPicker(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Refresh Interval',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 16),
              ...[2, 3, 5, 10].map((seconds) {
                return ListTile(
                  title: Text('$seconds seconds'),
                  trailing: seconds == 3 ? const Icon(Icons.check) : null,
                  onTap: () {
                    Navigator.pop(context);
                    // TODO: Update refresh interval
                  },
                );
              }),
            ],
          ),
        );
      },
    );
  }

  void _showServerSettings(BuildContext context) {
    final controller = TextEditingController(text: '192.168.1.100');

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Server Address'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: 'Enter IP address',
            prefixIcon: Icon(Icons.wifi),
          ),
          keyboardType: TextInputType.number,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              // TODO: Update server address
              Navigator.pop(context);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                gradient: AppColors.primaryGradient,
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.security_rounded,
                color: Colors.white,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Alertix'),
                Text(
                  'Version 1.0.0',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.normal,
                  ),
                ),
              ],
            ),
          ],
        ),
        content: const Text(
          'Alertix is a smart supermarket theft detection system '
          'that uses AI-powered camera monitoring to detect and alert '
          'suspicious activities in real-time.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showLogoutConfirmation(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sign Out'),
        content: const Text('Are you sure you want to sign out?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              final authService = ref.read(authServiceProvider);
              await authService.signOut();
              ref.read(userModelProvider.notifier).clearUser();
              onLogout();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.error,
            ),
            child: const Text('Sign Out'),
          ),
        ],
      ),
    );
  }
}
