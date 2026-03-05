import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../theme/ebs_colors.dart';
import '../../../providers/gfx_settings_provider.dart';
import '../../common/ebs_toggle.dart';
import '../../common/ebs_dropdown.dart';
import '../../common/setting_row.dart';

class BrandingSection extends ConsumerWidget {
  const BrandingSection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gfx = ref.watch(gfxSettingsProvider);

    return Column(
      children: [
        SettingRow(
          label: 'Sponsor Logo 1',
          child: _DropZone(),
        ),
        SettingRow(
          label: 'Sponsor Logo 2',
          child: _DropZone(),
        ),
        SettingRow(
          label: 'Vanity Text',
          child: Container(
            width: 150,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.05),
              border: Border.all(color: EbsColors.glassBorder),
              borderRadius: BorderRadius.circular(EbsColors.borderRadiusSm),
            ),
            child: Text(
              gfx.vanityText,
              style: const TextStyle(fontSize: 12, color: EbsColors.textPrimary),
            ),
          ),
        ),
        SettingRow(
          label: 'Replace w/ Game Variant',
          child: EbsToggle(
            value: gfx.replaceWithGameVariant,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleReplaceWithGameVariant(),
          ),
        ),
        SettingRow(
          label: 'Blinds Display',
          child: EbsDropdown(
            value: gfx.blindsDisplay,
            items: const ['Never', 'Every Hand', 'New Level', 'With Strip'],
            width: 120,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setBlindsDisplay(v),
          ),
        ),
        SettingRow(
          label: 'Show Hand # w/ Blinds',
          child: EbsToggle(
            value: gfx.showHandWithBlinds,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleShowHandWithBlinds(),
          ),
        ),
      ],
    );
  }
}

class _DropZone extends StatelessWidget {
  const _DropZone();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 120,
      height: 40,
      decoration: BoxDecoration(
        border: Border.all(color: Colors.white.withValues(alpha: 0.2)),
        borderRadius: BorderRadius.circular(EbsColors.borderRadiusSm),
      ),
      alignment: Alignment.center,
      child: const Text(
        'DROP 120\u00D740',
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.6,
          color: EbsColors.textMuted,
        ),
      ),
    );
  }
}
