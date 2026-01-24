import 'package:flutter/material.dart';
import '../../models/camera_status.dart';
import '../../core/theme/app_colors.dart';

class CameraStatusIndicator extends StatelessWidget {
  const CameraStatusIndicator({
    super.key,
    required this.status,
  });
  final CameraStatus status;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    Color statusColor;
    String statusText;
    IconData statusIcon;

    switch (status.status) {
      case CameraConnectionStatus.online:
        statusColor = AppColors.cameraOnline;
        statusText = 'Camera Online';
        statusIcon = Icons.videocam;
        break;
      case CameraConnectionStatus.offline:
        statusColor = AppColors.cameraOffline;
        statusText = 'Camera Offline';
        statusIcon = Icons.videocam_off;
        break;
      case CameraConnectionStatus.connecting:
        statusColor = AppColors.cameraConnecting;
        statusText = 'Connecting...';
        statusIcon = Icons.sync;
        break;
      case CameraConnectionStatus.error:
        statusColor = AppColors.error;
        statusText = 'Connection Error';
        statusIcon = Icons.error_outline;
        break;
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: statusColor,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: statusColor.withValues(alpha: 0.5),
                blurRadius: 4,
                spreadRadius: 1,
              ),
            ],
          ),
        ),
        const SizedBox(width: 8),
        Icon(
          statusIcon,
          size: 16,
          color: isDark
              ? AppColors.textSecondaryDark
              : AppColors.textSecondaryLight,
        ),
        const SizedBox(width: 4),
        Text(
          statusText,
          style: TextStyle(
            fontSize: 12,
            color: isDark
                ? AppColors.textSecondaryDark
                : AppColors.textSecondaryLight,
          ),
        ),
      ],
    );
  }
}
