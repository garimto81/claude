import 'package:flutter/material.dart';
import '../../theme/ebs_colors.dart';

enum IndicatorType { live, active, idle, warning }

class StatusIndicator extends StatefulWidget {
  final IndicatorType type;
  final double size;

  const StatusIndicator({
    super.key,
    required this.type,
    this.size = 8,
  });

  @override
  State<StatusIndicator> createState() => _StatusIndicatorState();
}

class _StatusIndicatorState extends State<StatusIndicator>
    with SingleTickerProviderStateMixin {
  late final AnimationController? _controller;
  late final Animation<double>? _animation;

  bool get _shouldAnimate =>
      widget.type == IndicatorType.live || widget.type == IndicatorType.active;

  @override
  void initState() {
    super.initState();
    if (_shouldAnimate) {
      _controller = AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 1500),
      )..repeat(reverse: true);
      _animation = Tween<double>(begin: 1.0, end: 0.35).animate(
        CurvedAnimation(parent: _controller!, curve: Curves.easeInOut),
      );
    } else {
      _controller = null;
      _animation = null;
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  Color get _color {
    return switch (widget.type) {
      IndicatorType.live => EbsColors.danger,
      IndicatorType.active => EbsColors.success,
      IndicatorType.idle => EbsColors.textMuted,
      IndicatorType.warning => EbsColors.warning,
    };
  }

  double get _glowRadius {
    return switch (widget.type) {
      IndicatorType.live => 8.0,
      IndicatorType.active => 6.0,
      IndicatorType.warning => 5.0,
      IndicatorType.idle => 0.0,
    };
  }

  @override
  Widget build(BuildContext context) {
    final color = _color;
    final glow = _glowRadius;

    final dot = Container(
      width: widget.size,
      height: widget.size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
        boxShadow: glow > 0
            ? [
                BoxShadow(
                  color: color.withValues(alpha: 0.7),
                  blurRadius: glow,
                  spreadRadius: 1,
                ),
              ]
            : null,
      ),
    );

    if (_animation case final anim?) {
      return AnimatedBuilder(
        animation: anim,
        builder: (_, child) => Opacity(opacity: anim.value, child: child),
        child: dot,
      );
    }
    return dot;
  }
}
