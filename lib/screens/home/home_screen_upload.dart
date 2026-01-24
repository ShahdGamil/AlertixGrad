import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';

import '../../core/theme/app_colors.dart';
import '../../models/models.dart';
import '../../providers/cameras_provider.dart';
import '../../services/alert_service.dart';
import '../../services/detection_service.dart';
import '../widgets/detection_overlay.dart';

class HomeScreenUpload extends ConsumerStatefulWidget {
  const HomeScreenUpload({super.key});

  @override
  ConsumerState<HomeScreenUpload> createState() => _HomeScreenUploadState();
}

class _HomeScreenUploadState extends ConsumerState<HomeScreenUpload> {
  final ImagePicker _picker = ImagePicker();
  XFile? _selectedImage;
  CameraModel? _selectedCamera;
  DetectionResult? _detectionResult;
  bool _isProcessing = false;
  bool _isPickingImage = false;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final camerasAsync = ref.watch(camerasProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Image Detection'),
        backgroundColor: isDark ? AppColors.backgroundDark : AppColors.backgroundLight,
        elevation: 0,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Selected Camera Display
              if (_selectedCamera != null)
                _buildSelectedCameraHeader(isDark),

              if (_selectedCamera != null)
                const SizedBox(height: 16),

              // Camera Selection - Horizontal Scrollable Cards
              _buildCameraSelection(camerasAsync, isDark),
              const SizedBox(height: 20),

              // Image Upload Section
              _buildImageUploadSection(isDark),
              const SizedBox(height: 20),

              // Detection Button
              _buildDetectionButton(isDark),

              // Detection Results
              if (_detectionResult != null) ...[
                const SizedBox(height: 20),
                _buildDetectionResults(isDark),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSelectedCameraHeader(bool isDark) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDark
              ? [AppColors.primaryDark, AppColors.primaryDark.withValues(alpha: 0.7)]
              : [AppColors.primary, AppColors.primary.withValues(alpha: 0.7)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: (isDark ? AppColors.primaryDark : AppColors.primary)
                .withValues(alpha: 0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.videocam_rounded,
              color: Colors.white,
              size: 24,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Current Camera',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.white.withValues(alpha: 0.9),
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _selectedCamera!.name,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                Text(
                  _selectedCamera!.location,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.white.withValues(alpha: 0.8),
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: _selectedCamera!.isActive
                  ? AppColors.success
                  : Colors.grey,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              _selectedCamera!.isActive ? 'Active' : 'Inactive',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCameraSelection(
    AsyncValue<List<CameraModel>> camerasAsync,
    bool isDark,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: Row(
            children: [
              Icon(
                Icons.videocam_outlined,
                color: isDark ? AppColors.primaryDark : AppColors.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'Select Camera',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: isDark ? Colors.white : AppColors.textPrimaryLight,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        camerasAsync.when(
          data: (cameras) {
            if (cameras.isEmpty) {
              return Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.info.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: AppColors.info.withValues(alpha: 0.3),
                    width: 1,
                  ),
                ),
                child: Column(
                  children: [
                    Icon(
                      Icons.videocam_off_outlined,
                      color: AppColors.info,
                      size: 48,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'No cameras added yet',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: isDark ? Colors.white : AppColors.textPrimaryLight,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Go to Cameras tab to add your first camera',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 13,
                        color: isDark
                            ? AppColors.textSecondaryDark
                            : AppColors.textSecondaryLight,
                      ),
                    ),
                  ],
                ),
              );
            }

            return SizedBox(
              height: 120,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: cameras.length,
                itemBuilder: (context, index) {
                  final camera = cameras[index];
                  final isSelected = _selectedCamera?.id == camera.id;

                  return Padding(
                    padding: EdgeInsets.only(
                      right: index < cameras.length - 1 ? 12 : 0,
                    ),
                    child: _buildCameraCard(camera, isSelected, isDark),
                  );
                },
              ),
            );
          },
          loading: () => const Center(
            child: Padding(
              padding: EdgeInsets.all(32),
              child: CircularProgressIndicator(),
            ),
          ),
          error: (error, _) => Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.error.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                Icon(Icons.error_outline, color: AppColors.error),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Error loading cameras',
                    style: TextStyle(color: AppColors.error),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCameraCard(CameraModel camera, bool isSelected, bool isDark) {
    final canSelect = camera.isActive;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: canSelect ? () {
          setState(() {
            _selectedCamera = camera;
            _detectionResult = null; // Clear results when changing camera
          });
        } : null,
        borderRadius: BorderRadius.circular(16),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: 160,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: !canSelect
                ? (isDark ? Colors.grey.shade800 : Colors.grey.shade300)
                : isSelected
                    ? (isDark ? AppColors.primaryDark : AppColors.primary)
                    : (isDark ? AppColors.cardDark : AppColors.cardLight),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: !canSelect
                  ? Colors.grey
                  : isSelected
                      ? (isDark ? AppColors.primaryDark : AppColors.primary)
                      : (isDark
                          ? AppColors.cardDark.withValues(alpha: 0.3)
                          : AppColors.cardLight.withValues(alpha: 0.3)),
              width: isSelected ? 2 : 1,
            ),
            boxShadow: isSelected && canSelect
                ? [
                    BoxShadow(
                      color: (isDark ? AppColors.primaryDark : AppColors.primary)
                          .withValues(alpha: 0.4),
                      blurRadius: 12,
                      offset: const Offset(0, 4),
                    ),
                  ]
                : [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.05),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
          ),
          child: Opacity(
            opacity: canSelect ? 1.0 : 0.5,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Icon(
                      canSelect ? Icons.videocam_rounded : Icons.videocam_off_rounded,
                      color: isSelected
                          ? Colors.white
                          : (camera.isActive ? AppColors.success : Colors.grey),
                      size: 28,
                    ),
                    if (isSelected && canSelect)
                      const Icon(
                        Icons.check_circle_rounded,
                        color: Colors.white,
                        size: 20,
                      ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      camera.name,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: isSelected
                            ? Colors.white
                            : !canSelect
                                ? Colors.grey
                                : (isDark ? Colors.white : AppColors.textPrimaryLight),
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          Icons.location_on_outlined,
                          size: 12,
                          color: isSelected
                              ? Colors.white.withValues(alpha: 0.8)
                              : !canSelect
                                  ? Colors.grey
                                  : (isDark
                                      ? AppColors.textSecondaryDark
                                      : AppColors.textSecondaryLight),
                        ),
                        const SizedBox(width: 4),
                        Expanded(
                          child: Text(
                            camera.location,
                            style: TextStyle(
                              fontSize: 11,
                              color: isSelected
                                  ? Colors.white.withValues(alpha: 0.8)
                                  : !canSelect
                                      ? Colors.grey
                                      : (isDark
                                          ? AppColors.textSecondaryDark
                                          : AppColors.textSecondaryLight),
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildImageUploadSection(bool isDark) {
    final canUpload = _selectedCamera != null && !_isPickingImage && !_isProcessing;

    return Card(
      elevation: 2,
      color: isDark ? AppColors.cardDark : AppColors.cardLight,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.image_rounded,
                  color: isDark ? AppColors.primaryDark : AppColors.primary,
                ),
                const SizedBox(width: 12),
                Text(
                  'Upload Image',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: isDark ? Colors.white : AppColors.textPrimaryLight,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            if (_selectedImage == null) ...[
              // Take Snapshot button - directly opens camera
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: canUpload ? () => _pickImage(ImageSource.camera) : null,
                  icon: _isPickingImage
                      ? const SizedBox(
                          width: 28,
                          height: 28,
                          child: CircularProgressIndicator(
                            strokeWidth: 3,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : const Icon(Icons.camera_alt_rounded, size: 28),
                  label: Text(_isPickingImage ? 'Opening Camera...' : 'Take Snapshot'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: canUpload
                        ? (isDark ? AppColors.primaryDark : AppColors.primary)
                        : Colors.grey,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 20),
                    textStyle: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: canUpload ? 4 : 0,
                  ),
                ),
              ),
              const SizedBox(height: 12),
              // Upload from Gallery button
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: canUpload ? () => _pickImage(ImageSource.gallery) : null,
                  icon: _isPickingImage
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                          ),
                        )
                      : const Icon(Icons.photo_library_rounded, size: 24),
                  label: Text(_isPickingImage ? 'Opening Gallery...' : 'Upload from Gallery'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: canUpload
                        ? (isDark ? AppColors.primaryDark : AppColors.primary)
                        : Colors.grey,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    textStyle: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w500,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    side: BorderSide(
                      color: canUpload
                          ? (isDark ? AppColors.primaryDark : AppColors.primary)
                          : Colors.grey,
                      width: 1.5,
                    ),
                  ),
                ),
              ),
              if (!canUpload) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.warning.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: AppColors.warning.withValues(alpha: 0.3),
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.info_outline,
                        color: AppColors.warning,
                        size: 20,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          'Please select a camera first',
                          style: TextStyle(
                            fontSize: 13,
                            color: isDark
                                ? AppColors.textSecondaryDark
                                : AppColors.textSecondaryLight,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ] else ...[
              // Show selected image with detection overlay
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Stack(
                    children: [
                      // Conditional image display for web/mobile
                      if (kIsWeb)
                        Image.network(
                          _selectedImage!.path,
                          fit: BoxFit.cover,
                          width: double.infinity,
                        )
                      else
                        Image.file(
                          File(_selectedImage!.path),
                          fit: BoxFit.cover,
                          width: double.infinity,
                        ),

                      // Detection overlay
                      if (_detectionResult != null &&
                          _detectionResult!.theftDetected)
                        DetectionOverlay(
                          boundingBoxes: _detectionResult!.boundingBoxes,
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              TextButton.icon(
                onPressed: _clearImage,
                icon: const Icon(Icons.close),
                label: const Text('Remove Image'),
                style: TextButton.styleFrom(
                  foregroundColor: AppColors.error,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDetectionButton(bool isDark) {
    final canDetect = _selectedImage != null && _selectedCamera != null && !_isProcessing;

    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        onPressed: canDetect ? _processDetection : null,
        icon: _isProcessing
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                ),
              )
            : const Icon(Icons.search_rounded, size: 24),
        label: Text(_isProcessing ? 'Processing...' : 'Detect Theft'),
        style: ElevatedButton.styleFrom(
          backgroundColor: canDetect
              ? (isDark ? AppColors.primaryDark : AppColors.primary)
              : Colors.grey,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 18),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: canDetect ? 4 : 0,
        ),
      ),
    );
  }

  Widget _buildDetectionResults(bool isDark) {
    return Card(
      elevation: 2,
      color: isDark ? AppColors.cardDark : AppColors.cardLight,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  _detectionResult!.theftDetected
                      ? Icons.warning_rounded
                      : Icons.check_circle_rounded,
                  color: _detectionResult!.theftDetected
                      ? AppColors.error
                      : AppColors.success,
                ),
                const SizedBox(width: 12),
                Text(
                  'Detection Results',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: isDark ? Colors.white : AppColors.textPrimaryLight,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            _buildResultItem(
              icon: Icons.shield_outlined,
              label: 'Status',
              value: _detectionResult!.theftDetected
                  ? 'THEFT DETECTED'
                  : 'No Threat',
              valueColor: _detectionResult!.theftDetected
                  ? AppColors.error
                  : AppColors.success,
              isDark: isDark,
            ),

            if (_detectionResult!.overallConfidence != null) ...[
              const SizedBox(height: 12),
              _buildResultItem(
                icon: Icons.analytics_outlined,
                label: 'Confidence',
                value: '${(_detectionResult!.overallConfidence! * 100).toStringAsFixed(1)}%',
                valueColor: isDark ? Colors.white : AppColors.textPrimaryLight,
                isDark: isDark,
              ),
            ],

            if (_detectionResult!.description != null) ...[
              const SizedBox(height: 12),
              _buildResultItem(
                icon: Icons.description_outlined,
                label: 'Description',
                value: _detectionResult!.description!,
                valueColor: isDark ? Colors.white : AppColors.textPrimaryLight,
                isDark: isDark,
              ),
            ],

            if (_detectionResult!.boundingBoxes.isNotEmpty) ...[
              const SizedBox(height: 12),
              _buildResultItem(
                icon: Icons.location_searching,
                label: 'Detections',
                value: '${_detectionResult!.boundingBoxes.length} object(s)',
                valueColor: isDark ? Colors.white : AppColors.textPrimaryLight,
                isDark: isDark,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildResultItem({
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
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  color: isDark
                      ? AppColors.textSecondaryDark
                      : AppColors.textSecondaryLight,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: valueColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Future<void> _pickImage(ImageSource source) async {
    // Prevent multiple simultaneous picks
    if (_isPickingImage) return;

    try {
      // Check if camera is selected
      if (_selectedCamera == null) {
        _showSnackBar('Please select a camera first', AppColors.warning);
        return;
      }

      // Check if selected camera is active
      if (!_selectedCamera!.isActive) {
        _showSnackBar(
          'Selected camera is inactive. Please activate it first.',
          AppColors.error,
        );
        return;
      }

      setState(() => _isPickingImage = true);

      // Request permissions based on source
      bool permissionGranted = false;
      if (source == ImageSource.camera) {
        permissionGranted = await _requestCameraPermission();
      } else {
        permissionGranted = await _requestStoragePermission();
      }

      if (!permissionGranted) {
        setState(() => _isPickingImage = false);
        return;
      }

      final image = await _picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      if (image != null && _selectedCamera != null) {
        // Validate image file
        final file = File(image.path);
        final fileExists = await file.exists();
        final fileSize = fileExists ? await file.length() : 0;

        if (!fileExists || fileSize == 0) {
          _showSnackBar('Invalid image file. Please try again.', AppColors.error);
          setState(() => _isPickingImage = false);
          return;
        }

        // Rename file with camera name and timestamp
        final renamedImage = await _renameImageFile(image, _selectedCamera!.name);

        setState(() {
          _selectedImage = renamedImage;
          _detectionResult = null; // Clear previous results
          _isPickingImage = false;
        });

        final message = source == ImageSource.camera
            ? 'Snapshot captured for ${_selectedCamera!.name}'
            : 'Image uploaded for ${_selectedCamera!.name}';

        _showSnackBar(message, AppColors.success);
      } else {
        setState(() => _isPickingImage = false);
      }
    } catch (e) {
      setState(() => _isPickingImage = false);
      _showSnackBar(
        'Error: ${e.toString()}',
        AppColors.error,
      );
    }
  }

  Future<bool> _requestCameraPermission() async {
    final status = await Permission.camera.request();

    if (status.isGranted) {
      return true;
    } else if (status.isDenied) {
      _showSnackBar(
        'Camera permission denied. Please enable it in settings.',
        AppColors.error,
      );
      return false;
    } else if (status.isPermanentlyDenied) {
      final shouldOpen = await _showPermissionDialog(
        'Camera Permission Required',
        'Camera access is required to take snapshots. Please enable it in app settings.',
      );
      if (shouldOpen) {
        await openAppSettings();
      }
      return false;
    }
    return false;
  }

  Future<bool> _requestStoragePermission() async {
    if (Platform.isAndroid) {
      // Android 13+ (API 33+) uses photos permission
      // Android 12 and below use storage permission

      // First check if we already have permission
      var photosStatus = await Permission.photos.status;
      var storageStatus = await Permission.storage.status;

      if (photosStatus.isGranted || storageStatus.isGranted) {
        return true;
      }

      // Request photos permission (this works for Android 13+)
      photosStatus = await Permission.photos.request();
      if (photosStatus.isGranted) {
        return true;
      }

      // Request storage permission (for Android 12 and below)
      storageStatus = await Permission.storage.request();
      if (storageStatus.isGranted) {
        return true;
      }

      // Handle denied permissions
      if (photosStatus.isPermanentlyDenied || storageStatus.isPermanentlyDenied) {
        final shouldOpen = await _showPermissionDialog(
          'Photos Permission Required',
          'Photo library access is required to upload images. Please enable it in app settings.',
        );
        if (shouldOpen) {
          await openAppSettings();
        }
      } else {
        _showSnackBar(
          'Photo library permission denied. Please enable it to upload images.',
          AppColors.error,
        );
      }
      return false;
    }

    // iOS/Web handle permissions differently
    return true;
  }

  Future<bool> _showPermissionDialog(String title, String message) async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
            ),
            child: const Text('Open Settings'),
          ),
        ],
      ),
    );
    return result ?? false;
  }

  void _showSnackBar(String message, Color backgroundColor) {
    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              backgroundColor == AppColors.success
                  ? Icons.check_circle
                  : backgroundColor == AppColors.warning
                      ? Icons.warning_rounded
                      : Icons.error_outline,
              color: Colors.white,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        backgroundColor: backgroundColor,
      ),
    );
  }

  Future<XFile> _renameImageFile(XFile originalFile, String cameraName) async {
    try {
      // Create timestamp in format: yyyyMMdd_HHmmss
      final timestamp = DateFormat('yyyyMMdd_HHmmss').format(DateTime.now());

      // Clean camera name (remove spaces and special characters)
      final cleanCameraName = cameraName.replaceAll(RegExp(r'[^\w]'), '');

      // Create new filename: CameraName_timestamp.jpg
      final newFileName = '${cleanCameraName}_$timestamp.jpg';

      // Get temporary directory
      final directory = await getTemporaryDirectory();
      final newPath = path.join(directory.path, newFileName);

      // Copy file to new path with new name
      final bytes = await originalFile.readAsBytes();
      final newFile = File(newPath);
      await newFile.writeAsBytes(bytes);

      return XFile(newPath);
    } catch (e) {
      // If renaming fails, return original file
      debugPrint('Error renaming file: $e');
      return originalFile;
    }
  }

  void _clearImage() {
    setState(() {
      _selectedImage = null;
      _detectionResult = null;
    });
  }

  Future<void> _processDetection() async {
    if (_selectedImage == null || _selectedCamera == null) return;

    setState(() => _isProcessing = true);

    try {
      final detectionService = DetectionService();
      final result = await detectionService.detectImageUpload(
        imageFile: File(_selectedImage!.path),
        cameraId: _selectedCamera!.id,
        cameraName: _selectedCamera!.name,
      );

      setState(() {
        _detectionResult = result;
      });

      // Auto-create alert if theft detected with sufficient confidence
      if (result.theftDetected && (result.overallConfidence ?? 0.0) >= 0.6) {
        final alertService = AlertService();
        final alert = AlertModel.fromDetectionResult(result);
        await alertService.saveAlert(alert);

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Row(
                children: [
                  const Icon(Icons.warning_rounded, color: Colors.white),
                  const SizedBox(width: 12),
                  const Expanded(child: Text('Theft detected! Alert created.')),
                ],
              ),
              backgroundColor: AppColors.error,
              duration: const Duration(seconds: 4),
            ),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.white),
                  SizedBox(width: 12),
                  Text('No suspicious activity detected'),
                ],
              ),
              backgroundColor: AppColors.success,
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Detection failed: $e'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    } finally {
      setState(() => _isProcessing = false);
    }
  }
}
