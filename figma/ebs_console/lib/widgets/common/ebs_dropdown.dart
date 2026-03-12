import 'package:flutter/material.dart';
import '../../theme/ebs_colors.dart';

class EbsDropdown extends StatelessWidget {
  final String value;
  final List<String> items;
  final ValueChanged<String>? onChanged;
  final double? width;

  const EbsDropdown({
    super.key,
    required this.value,
    required this.items,
    this.onChanged,
    this.width,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
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
            icon: const Icon(Icons.expand_more, size: 16, color: EbsColors.textMuted),
            items: items
                .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                .toList(),
            onChanged: (v) {
              if (v != null) onChanged?.call(v);
            },
          ),
        ),
      ),
    );
  }
}
