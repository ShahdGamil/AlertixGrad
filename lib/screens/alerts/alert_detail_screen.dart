import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:intl/intl.dart';
import 'package:photo_view/photo_view.dart';
import '../../providers/detection_provider.dart';
import '../../models/models.dart';
import '../../core/theme/app_colors.dart';
import '../widgets/detection_overlay.dart';

class AlertDetailScreen extends ConsumerWidget {
  const AlertDetailScreen({
    super.key,
    required this.alertId,
    this.alert,
  });
  final String alertId;
  final AlertModel? alert;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    // Use provided alert or fetch from provider
    final alertData = alert ??
        ref.watch(alertsProvider).valueOrNull?.firstWhere(
              (a) => a.id == alertId,
              orElse: () => throw Exception('Alert not found'),
            );

    if (alertData == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(
          child: Text('Alert not found'),
        ),
      );
    }

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // App Bar with Image
          SliverAppBar(
            expandedHeight: 300,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              background: Stack(
                fit: StackFit.expand,
                children: [
                  GestureDetector(
                    onTap: () => _showFullScreenImage(context, alertData),
                    child: Hero(
                      tag: 'alert_${alertData.id}',
                      child: CachedNetworkImage(
                        imageUrl: alertData.imageUrl,
                        fit: BoxFit.cover,
                        placeholder: (_, __) => Container(
                          color: isDark
                              ? AppColors.surfaceDark
                              : AppColors.inputFillLight,
                        ),
                        errorWidget: (_, __, ___) => Container(
                          color: isDark
                              ? AppColors.surfaceDark
                              : AppColors.inputFillLight,
                          child: const Icon(Icons.image_not_supported),
                        ),
                      ),
                    ),
                  ),
                  // Detection overlay
                  if (alertData.boundingBoxes.isNotEmpty)
                    DetectionOverlay(boundingBoxes: alertData.boundingBoxes),
                  // Gradient overlay
                  Positioned(
                    bottom: 0,
                    left: 0,
                    right: 0,
                    child: Container(
                      height: 100,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            Colors.transparent,
                            Colors.black.withValues(alpha: 0.7),
                          ],
                        ),
                      ),
                    ),
                  ),
                  // Tap to zoom hint
                  Positioned(
                    bottom: 16,
                    right: 16,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.black.withValues(alpha: 0.5),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.zoom_in,
                            color: Colors.white,
                            size: 16,
                          ),
                          SizedBox(width: 4),
                          Text(
                            'Tap to zoom',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Content
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Status badges
                  Row(
                    children: [
                      _buildSeverityBadge(alertData),
                      const SizedBox(width: 8),
                      _buildStatusBadge(alertData),
                      const Spacer(),
                      _buildActionButtons(context, ref, alertData),
                    ],
                  ),
                  const SizedBox(height: 20),

                  // Title
                  Text(
                    'Theft Detection Alert',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: isDark ? Colors.white : AppColors.textPrimaryLight,
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Timestamp
                  Row(
                    children: [
                      Icon(
                        Icons.access_time,
                        size: 16,
                        color: isDark
                            ? AppColors.textSecondaryDark
                            : AppColors.textSecondaryLight,
                      ),
                      const SizedBox(width: 6),
                      Text(
                        DateFormat('EEEE, MMMM d, yyyy - HH:mm:ss')
                            .format(alertData.timestamp),
                        style: TextStyle(
                          fontSize: 14,
                          color: isDark
                              ? AppColors.textSecondaryDark
                              : AppColors.textSecondaryLight,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Detection Details Card
                  _buildDetailCard(
                    context,
                    isDark,
                    title: 'Detection Details',
                    icon: Icons.analytics_outlined,
                    children: [
                      _buildDetailRow(
                        'Status',
                        alertData.theftDetected ? 'Theft Detected' : 'Normal',
                        color: alertData.theftDetected
                            ? AppColors.error
                            : AppColors.success,
                      ),
                      if (alertData.confidence != null)
                        _buildDetailRow(
                          'Confidence',
                          '${(alertData.confidence! * 100).toStringAsFixed(1)}%',
                        ),
                      _buildDetailRow(
                        'Severity',
                        alertData.severityLabel,
                        color: _getSeverityColor(alertData.severity),
                      ),
                      _buildDetailRow(
                        'Objects Detected',
                        '${alertData.boundingBoxes.length}',
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Bounding Box Details
                  if (alertData.boundingBoxes.isNotEmpty)
                    _buildDetailCard(
                      context,
                      isDark,
                      title: 'Detected Objects',
                      icon: Icons.crop_free,
                      children: [
                        ...alertData.boundingBoxes.asMap().entries.map((entry) {
                          final index = entry.key;
                          final box = entry.value;
                          return Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              if (index > 0) const Divider(height: 24),
                              Text(
                                'Object ${index + 1}',
                                style: TextStyle(
                                  fontWeight: FontWeight.w600,
                                  color: isDark
                                      ? Colors.white
                                      : AppColors.textPrimaryLight,
                                ),
                              ),
                              const SizedBox(height: 8),
                              if (box.label != null)
                                _buildDetailRow('Label', box.label!),
                              _buildDetailRow(
                                'Confidence',
                                '${(box.confidence * 100).toStringAsFixed(1)}%',
                              ),
                              _buildDetailRow(
                                'Position',
                                'X: ${box.x.toStringAsFixed(2)}, Y: ${box.y.toStringAsFixed(2)}',
                              ),
                              _buildDetailRow(
                                'Size',
                                'W: ${box.width.toStringAsFixed(2)}, H: ${box.height.toStringAsFixed(2)}',
                              ),
                            ],
                          );
                        }),
                      ],
                    ),
                  const SizedBox(height: 16),

                  // Actions Card
                  _buildDetailCard(
                    context,
                    isDark,
                    title: 'Quick Actions',
                    icon: Icons.flash_on_outlined,
                    children: [
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: [
                          _buildActionChip(
                            context,
                            icon: Icons.share_outlined,
                            label: 'Share',
                            onTap: () {
                              // TODO: Share functionality
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                    content: Text(
                                        'Share functionality coming soon')),
                              );
                            },
                          ),
                          _buildActionChip(
                            context,
                            icon: Icons.download_outlined,
                            label: 'Download',
                            onTap: () {
                              // TODO: Download functionality
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                    content: Text(
                                        'Download functionality coming soon')),
                              );
                            },
                          ),
                          _buildActionChip(
                            context,
                            icon: Icons.report_outlined,
                            label: 'Report',
                            onTap: () {
                              // TODO: Report functionality
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                    content: Text(
                                        'Report functionality coming soon')),
                              );
                            },
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSeverityBadge(AlertModel alert) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: _getSeverityColor(alert.severity).withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.warning_amber_rounded,
            size: 16,
            color: _getSeverityColor(alert.severity),
          ),
          const SizedBox(width: 6),
          Text(
            alert.severityLabel,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: _getSeverityColor(alert.severity),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(AlertModel alert) {
    Color color;
    switch (alert.status) {
      case AlertStatus.active:
        color = AppColors.error;
        break;
      case AlertStatus.acknowledged:
        color = AppColors.warning;
        break;
      case AlertStatus.resolved:
        color = AppColors.success;
        break;
      case AlertStatus.dismissed:
        color = AppColors.textSecondaryLight;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        alert.statusLabel,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }

  Widget _buildActionButtons(
      BuildContext context, WidgetRef ref, AlertModel alert) {
    return PopupMenuButton<String>(
      icon: const Icon(Icons.more_vert),
      onSelected: (value) {
        switch (value) {
          case 'acknowledge':
            ref.read(alertsProvider.notifier).updateStatus(
                  alert.id,
                  AlertStatus.acknowledged,
                );
            break;
          case 'resolve':
            ref.read(alertsProvider.notifier).updateStatus(
                  alert.id,
                  AlertStatus.resolved,
                );
            break;
          case 'delete':
            ref.read(alertsProvider.notifier).deleteAlert(alert.id);
            Navigator.pop(context);
            break;
        }
      },
      itemBuilder: (context) => [
        const PopupMenuItem(
          value: 'acknowledge',
          child: Row(
            children: [
              Icon(Icons.check_circle_outline),
              SizedBox(width: 12),
              Text('Acknowledge'),
            ],
          ),
        ),
        const PopupMenuItem(
          value: 'resolve',
          child: Row(
            children: [
              Icon(Icons.done_all),
              SizedBox(width: 12),
              Text('Mark Resolved'),
            ],
          ),
        ),
        const PopupMenuItem(
          value: 'delete',
          child: Row(
            children: [
              Icon(Icons.delete_outline, color: AppColors.error),
              SizedBox(width: 12),
              Text('Delete', style: TextStyle(color: AppColors.error)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildDetailCard(
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

  Widget _buildDetailRow(String label, String value, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              color: AppColors.textSecondaryLight,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionChip(
    BuildContext context, {
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return ActionChip(
      avatar: Icon(icon, size: 18),
      label: Text(label),
      onPressed: onTap,
      backgroundColor:
          isDark ? AppColors.surfaceDark : AppColors.inputFillLight,
    );
  }

  Color _getSeverityColor(AlertSeverity severity) {
    switch (severity) {
      case AlertSeverity.critical:
        return AppColors.error;
      case AlertSeverity.high:
        return AppColors.alertOrange;
      case AlertSeverity.medium:
        return AppColors.warning;
      case AlertSeverity.low:
        return AppColors.info;
    }
  }

  void _showFullScreenImage(BuildContext context, AlertModel alert) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          backgroundColor: Colors.black,
          appBar: AppBar(
            backgroundColor: Colors.transparent,
            iconTheme: const IconThemeData(color: Colors.white),
          ),
          body: PhotoView(
            imageProvider: CachedNetworkImageProvider(alert.imageUrl),
            minScale: PhotoViewComputedScale.contained,
            maxScale: PhotoViewComputedScale.covered * 3,
            heroAttributes: PhotoViewHeroAttributes(tag: 'alert_${alert.id}'),
          ),
        ),
      ),
    );
  }
}
