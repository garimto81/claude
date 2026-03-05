import 'package:flutter/material.dart';
import '../../theme/ebs_colors.dart';

class PrecisionDropdown extends StatelessWidget {
  final String label;
  final String value;
  final ValueChanged<String>? onChanged;
  final List<String> items;

  const PrecisionDropdown({
    super.key,
    required this.label,
    required this.value,
    this.onChanged,
    this.items = const ['Exact', 'Smart', 'Smart+Extra'],
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(
            label,
            style: const TextStyle(fontSize: 11, color: EbsColors.textSecondary),
          ),
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 120,
          child: DropdownButtonHideUnderline(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.06),
                border: Border.all(color: EbsColors.glassBorder),
                borderRadius: BorderRadius.circular(EbsColors.borderRadiusSm),
              ),
              child: DropdownButton<String>(
                value: value,
                isExpanded: true,
                isDense: true,
                dropdownColor: EbsColors.bgSecondary,
                style: const TextStyle(fontSize: 11, color: EbsColors.textPrimary),
                icon: const Icon(Icons.expand_more, size: 14, color: EbsColors.textMuted),
                items: items
                    .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                    .toList(),
                onChanged: (v) {
                  if (v != null) onChanged?.call(v);
                },
              ),
            ),
          ),
        ),
      ],
    );
  }
}
