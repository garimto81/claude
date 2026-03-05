import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/ebs_colors.dart';

class SpinnerInput extends StatelessWidget {
  final double value;
  final double min;
  final double max;
  final double step;
  final String? suffix;
  final ValueChanged<double>? onChanged;
  final double width;

  const SpinnerInput({
    super.key,
    required this.value,
    this.min = 0,
    this.max = 100,
    this.step = 1,
    this.suffix,
    this.onChanged,
    this.width = 100,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _StepButton(
            icon: Icons.remove,
            onTap: value > min ? () => onChanged?.call((value - step).clamp(min, max)) : null,
          ),
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 5),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.06),
                border: Border.symmetric(
                  horizontal: BorderSide(color: EbsColors.glassBorder),
                ),
              ),
              alignment: Alignment.center,
              child: Text(
                suffix != null
                    ? '${_formatValue(value)}$suffix'
                    : _formatValue(value),
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 11,
                  color: EbsColors.accentGold,
                ),
              ),
            ),
          ),
          _StepButton(
            icon: Icons.add,
            onTap: value < max ? () => onChanged?.call((value + step).clamp(min, max)) : null,
          ),
        ],
      ),
    );
  }

  String _formatValue(double v) {
    if (v == v.roundToDouble()) return v.toInt().toString();
    return v.toStringAsFixed(1);
  }
}

class _StepButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onTap;

  const _StepButton({required this.icon, this.onTap});

  @override
  Widget build(BuildContext context) {
    final enabled = onTap != null;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 24,
        height: 26,
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: enabled ? 0.08 : 0.03),
          border: Border.all(color: EbsColors.glassBorder),
          borderRadius: BorderRadius.circular(EbsColors.borderRadiusSm),
        ),
        alignment: Alignment.center,
        child: Icon(
          icon,
          size: 12,
          color: enabled ? EbsColors.textSecondary : EbsColors.textMuted,
        ),
      ),
    );
  }
}
