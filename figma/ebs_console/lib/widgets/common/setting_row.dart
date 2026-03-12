import 'package:flutter/material.dart';
import '../../theme/ebs_colors.dart';

class SettingRow extends StatelessWidget {
  final String label;
  final Widget child;

  const SettingRow({super.key, required this.label, required this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 7),
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(color: Color(0x0AFFFFFF), width: 1),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: const TextStyle(fontSize: 12, color: EbsColors.textSecondary),
            ),
          ),
          const SizedBox(width: 8),
          child,
        ],
      ),
    );
  }
}
