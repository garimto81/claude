import 'package:flutter/material.dart';
import '../../theme/ebs_colors.dart';

class EbsButton extends StatefulWidget {
  final String text;
  final VoidCallback? onPressed;
  final bool small;

  const EbsButton({
    super.key,
    required this.text,
    this.onPressed,
    this.small = false,
  });

  @override
  State<EbsButton> createState() => _EbsButtonState();
}

class _EbsButtonState extends State<EbsButton> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        curve: Curves.easeOut,
        decoration: BoxDecoration(
          color: _hovered
              ? EbsColors.neonGlow
              : Colors.white.withValues(alpha: 0.06),
          border: Border.all(
            color: _hovered
                ? EbsColors.accentBlue.withValues(alpha: 0.4)
                : EbsColors.glassBorder,
          ),
          borderRadius: BorderRadius.circular(EbsColors.borderRadiusSm),
          boxShadow: _hovered
              ? [
                  BoxShadow(
                    color: EbsColors.accentBlue.withValues(alpha: 0.2),
                    blurRadius: 8,
                    spreadRadius: 0,
                  ),
                ]
              : null,
        ),
        child: InkWell(
          onTap: widget.onPressed,
          borderRadius: BorderRadius.circular(EbsColors.borderRadiusSm),
          hoverColor: Colors.transparent,
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: widget.small ? 10 : 14,
              vertical: widget.small ? 4 : 6,
            ),
            child: Text(
              widget.text,
              style: TextStyle(
                fontSize: widget.small ? 11 : 12,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.24,
                color: _hovered ? EbsColors.accentBlue : EbsColors.textPrimary,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
