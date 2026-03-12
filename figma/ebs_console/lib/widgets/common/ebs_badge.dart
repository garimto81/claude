import 'package:flutter/material.dart';
import '../../theme/ebs_colors.dart';

enum BadgeVariant { gold, blue, neon, success, danger, muted }

class EbsBadge extends StatelessWidget {
  final String text;
  final BadgeVariant variant;
  final Widget? leading;
  final bool isMono;

  const EbsBadge({
    super.key,
    required this.text,
    required this.variant,
    this.leading,
    this.isMono = false,
  });

  @override
  Widget build(BuildContext context) {
    final (bg, fg, border) = _colors;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: bg,
        border: Border.all(color: border),
        borderRadius: BorderRadius.circular(100),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (leading != null) ...[leading!, const SizedBox(width: 4)],
          Text(
            text,
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.6,
              color: fg,
              fontFamily: isMono ? 'JetBrains Mono' : null,
            ),
          ),
        ],
      ),
    );
  }

  (Color bg, Color fg, Color border) get _colors {
    switch (variant) {
      case BadgeVariant.gold:
        return (
          EbsColors.accentGold.withValues(alpha: 0.18),
          EbsColors.accentGold,
          EbsColors.accentGold.withValues(alpha: 0.35),
        );
      case BadgeVariant.blue:
        return (
          EbsColors.accentBlue.withValues(alpha: 0.15),
          EbsColors.accentBlue,
          EbsColors.accentBlue.withValues(alpha: 0.3),
        );
      case BadgeVariant.neon:
        return (
          EbsColors.accentNeon.withValues(alpha: 0.15),
          EbsColors.accentNeon,
          EbsColors.accentNeon.withValues(alpha: 0.3),
        );
      case BadgeVariant.success:
        return (
          EbsColors.success.withValues(alpha: 0.15),
          EbsColors.success,
          EbsColors.success.withValues(alpha: 0.3),
        );
      case BadgeVariant.danger:
        return (
          EbsColors.danger.withValues(alpha: 0.15),
          EbsColors.danger,
          EbsColors.danger.withValues(alpha: 0.3),
        );
      case BadgeVariant.muted:
        return (
          EbsColors.textMuted.withValues(alpha: 0.25),
          EbsColors.textMuted,
          EbsColors.textMuted.withValues(alpha: 0.4),
        );
    }
  }
}
