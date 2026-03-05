import 'package:flutter/material.dart';
import '../../theme/ebs_colors.dart';

class CollapsibleSection extends StatelessWidget {
  final String title;
  final bool isExpanded;
  final VoidCallback onToggle;
  final Widget child;

  const CollapsibleSection({
    super.key,
    required this.title,
    required this.isExpanded,
    required this.onToggle,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        GestureDetector(
          onTap: onToggle,
          child: Container(
            padding: const EdgeInsets.symmetric(
              horizontal: EbsColors.spacingMd,
              vertical: EbsColors.spacingSm,
            ),
            color: Colors.black.withValues(alpha: 0.2),
            child: Row(
              children: [
                AnimatedRotation(
                  turns: isExpanded ? 0.25 : 0.0,
                  duration: const Duration(milliseconds: 220),
                  curve: Curves.easeOutCubic,
                  child: const Icon(
                    Icons.chevron_right,
                    size: 16,
                    color: EbsColors.textMuted,
                  ),
                ),
                const SizedBox(width: 6),
                Text(
                  title.toUpperCase(),
                  style: const TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.0,
                    color: EbsColors.textMuted,
                  ),
                ),
              ],
            ),
          ),
        ),
        // Content with easeOutCubic
        AnimatedCrossFade(
          firstChild: Padding(
            padding: const EdgeInsets.all(EbsColors.spacingMd),
            child: child,
          ),
          secondChild: const SizedBox.shrink(),
          crossFadeState:
              isExpanded ? CrossFadeState.showFirst : CrossFadeState.showSecond,
          duration: const Duration(milliseconds: 220),
          firstCurve: Curves.easeOutCubic,
          secondCurve: Curves.easeInCubic,
          sizeCurve: Curves.easeOutCubic,
        ),
        const Divider(height: 1, color: EbsColors.glassBorder),
      ],
    );
  }
}
