import 'package:flutter/material.dart';
import '../../theme/ebs_colors.dart';

class EbsToggle extends StatelessWidget {
  final bool value;
  final ValueChanged<bool>? onChanged;

  const EbsToggle({super.key, required this.value, this.onChanged});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onChanged?.call(!value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeInOut,
        width: 40,
        height: 22,
        decoration: BoxDecoration(
          color: value
              ? EbsColors.accentBlue.withValues(alpha: 0.25)
              : Colors.white.withValues(alpha: 0.12),
          border: Border.all(
            color: value ? EbsColors.accentBlue : EbsColors.glassBorder,
          ),
          borderRadius: BorderRadius.circular(11),
          boxShadow: value
              ? [
                  BoxShadow(
                    color: EbsColors.accentBlue.withValues(alpha: 0.25),
                    blurRadius: 6,
                    spreadRadius: 0,
                  ),
                ]
              : null,
        ),
        child: AnimatedAlign(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeInOut,
          alignment: value ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            margin: const EdgeInsets.all(3),
            width: 14,
            height: 14,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: value ? EbsColors.accentBlue : EbsColors.textMuted,
              boxShadow: value
                  ? [
                      BoxShadow(
                        color: EbsColors.accentBlue.withValues(alpha: 0.5),
                        blurRadius: 4,
                      ),
                    ]
                  : null,
            ),
          ),
        ),
      ),
    );
  }
}
