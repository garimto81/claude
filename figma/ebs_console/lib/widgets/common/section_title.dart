import 'package:flutter/material.dart';
import '../../theme/ebs_colors.dart';

class SectionTitle extends StatelessWidget {
  final String text;
  final EdgeInsetsGeometry padding;

  const SectionTitle(
    this.text, {
    super.key,
    this.padding = const EdgeInsets.symmetric(horizontal: 8),
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: padding,
      child: Text(
        text.toUpperCase(),
        style: const TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.0,
          color: EbsColors.textMuted,
        ),
      ),
    );
  }
}
