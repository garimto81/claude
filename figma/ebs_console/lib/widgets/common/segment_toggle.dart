import 'package:flutter/material.dart';
import '../../theme/ebs_colors.dart';

class SegmentToggle extends StatelessWidget {
  final List<String> labels;
  final int selectedIndex;
  final ValueChanged<int>? onChanged;

  const SegmentToggle({
    super.key,
    required this.labels,
    required this.selectedIndex,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        border: Border.all(color: EbsColors.glassBorder),
        borderRadius: BorderRadius.circular(EbsColors.borderRadiusSm),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: List.generate(labels.length, (i) {
          final isActive = i == selectedIndex;
          return GestureDetector(
            onTap: () => onChanged?.call(i),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
              color: isActive ? EbsColors.textPrimary : Colors.transparent,
              child: Text(
                labels[i],
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.66,
                  color: isActive ? EbsColors.bgPrimary : EbsColors.textMuted,
                ),
              ),
            ),
          );
        }),
      ),
    );
  }
}
