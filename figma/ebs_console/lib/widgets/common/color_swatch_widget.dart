import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/ebs_colors.dart';

class ColorSwatchWidget extends StatelessWidget {
  final Color color;
  final String hexLabel;

  const ColorSwatchWidget({
    super.key,
    required this.color,
    required this.hexLabel,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 22,
          height: 22,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(3),
            border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          hexLabel,
          style: GoogleFonts.jetBrainsMono(
            fontSize: 11,
            color: EbsColors.textSecondary,
          ),
        ),
      ],
    );
  }
}
