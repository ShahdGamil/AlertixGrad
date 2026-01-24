import 'package:flutter/material.dart';
import '../../models/detection_result.dart';
import '../../core/theme/app_colors.dart';

class DetectionOverlay extends StatelessWidget {
  const DetectionOverlay({
    super.key,
    required this.boundingBoxes,
  });
  final List<BoundingBox> boundingBoxes;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Stack(
          children: [
            // Semi-transparent overlay
            Container(
              decoration: BoxDecoration(
                border: Border.all(
                  color: AppColors.error,
                  width: 3,
                ),
              ),
            ),
            // Bounding boxes
            ...boundingBoxes.map((box) {
              final pixelBox = box.toPixelCoordinates(
                constraints.maxWidth,
                constraints.maxHeight,
              );
              return Positioned(
                left: pixelBox.x,
                top: pixelBox.y,
                child: _BoundingBoxWidget(box: pixelBox),
              );
            }),
            // Alert indicator
            Positioned(
              top: 16,
              right: 16,
              child: _PulsingAlertIndicator(),
            ),
          ],
        );
      },
    );
  }
}

class _BoundingBoxWidget extends StatefulWidget {
  const _BoundingBoxWidget({required this.box});
  final BoundingBox box;

  @override
  State<_BoundingBoxWidget> createState() => _BoundingBoxWidgetState();
}

class _BoundingBoxWidgetState extends State<_BoundingBoxWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    )..repeat(reverse: true);

    _animation = Tween<double>(begin: 0.6, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          width: widget.box.width,
          height: widget.box.height,
          decoration: BoxDecoration(
            border: Border.all(
              color: AppColors.error.withValues(alpha: _animation.value),
              width: 2,
            ),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Stack(
            children: [
              // Corner indicators
              ..._buildCorners(),
              // Label
              if (widget.box.label != null || widget.box.confidence > 0)
                Positioned(
                  top: -24,
                  left: 0,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.error,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (widget.box.label != null) ...[
                          Text(
                            widget.box.label!,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          if (widget.box.confidence > 0)
                            const SizedBox(width: 6),
                        ],
                        if (widget.box.confidence > 0)
                          Text(
                            '${(widget.box.confidence * 100).toStringAsFixed(0)}%',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  List<Widget> _buildCorners() {
    const cornerSize = 12.0;
    const cornerWidth = 3.0;

    return [
      // Top-left corner
      Positioned(
        top: 0,
        left: 0,
        child: Container(
          width: cornerSize,
          height: cornerSize,
          decoration: const BoxDecoration(
            border: Border(
              top: BorderSide(color: AppColors.error, width: cornerWidth),
              left: BorderSide(color: AppColors.error, width: cornerWidth),
            ),
          ),
        ),
      ),
      // Top-right corner
      Positioned(
        top: 0,
        right: 0,
        child: Container(
          width: cornerSize,
          height: cornerSize,
          decoration: const BoxDecoration(
            border: Border(
              top: BorderSide(color: AppColors.error, width: cornerWidth),
              right: BorderSide(color: AppColors.error, width: cornerWidth),
            ),
          ),
        ),
      ),
      // Bottom-left corner
      Positioned(
        bottom: 0,
        left: 0,
        child: Container(
          width: cornerSize,
          height: cornerSize,
          decoration: const BoxDecoration(
            border: Border(
              bottom: BorderSide(color: AppColors.error, width: cornerWidth),
              left: BorderSide(color: AppColors.error, width: cornerWidth),
            ),
          ),
        ),
      ),
      // Bottom-right corner
      Positioned(
        bottom: 0,
        right: 0,
        child: Container(
          width: cornerSize,
          height: cornerSize,
          decoration: const BoxDecoration(
            border: Border(
              bottom: BorderSide(color: AppColors.error, width: cornerWidth),
              right: BorderSide(color: AppColors.error, width: cornerWidth),
            ),
          ),
        ),
      ),
    ];
  }
}

class _PulsingAlertIndicator extends StatefulWidget {
  @override
  State<_PulsingAlertIndicator> createState() => _PulsingAlertIndicatorState();
}

class _PulsingAlertIndicatorState extends State<_PulsingAlertIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _opacityAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    )..repeat();

    _scaleAnimation = Tween<double>(begin: 1, end: 1.5).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );

    _opacityAnimation = Tween<double>(begin: 1, end: 0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 60,
      height: 60,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Pulsing ring
          AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              return Transform.scale(
                scale: _scaleAnimation.value,
                child: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: AppColors.error
                          .withValues(alpha: _opacityAnimation.value),
                      width: 2,
                    ),
                  ),
                ),
              );
            },
          ),
          // Center circle
          Container(
            width: 40,
            height: 40,
            decoration: const BoxDecoration(
              color: AppColors.error,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.warning_rounded,
              color: Colors.white,
              size: 24,
            ),
          ),
        ],
      ),
    );
  }
}
