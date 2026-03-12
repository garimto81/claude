import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../providers/gfx_settings_provider.dart';
import '../../common/spinner_input.dart';
import '../../common/ebs_dropdown.dart';
import '../../common/setting_row.dart';

class LayoutSection extends ConsumerWidget {
  const LayoutSection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gfx = ref.watch(gfxSettingsProvider);

    return Column(
      children: [
        SettingRow(
          label: 'Board Position',
          child: EbsDropdown(
            value: gfx.boardPosition,
            items: const ['Left', 'Centre', 'Right'],
            width: 130,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setBoardPosition(v),
          ),
        ),
        SettingRow(
          label: 'Player Layout',
          child: EbsDropdown(
            value: gfx.playerLayout,
            items: const ['Horizontal', 'Vert/Bot/Spill', 'Vert/Bot/Fit', 'Vert/Top/Spill', 'Vert/Top/Fit'],
            width: 130,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setPlayerLayout(v),
          ),
        ),
        SettingRow(
          label: 'X Margin',
          child: SpinnerInput(
            value: gfx.xMargin * 100,
            min: 0, max: 20, step: 1, suffix: '%', width: 100,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setXMargin(v / 100),
          ),
        ),
        SettingRow(
          label: 'Top Margin',
          child: SpinnerInput(
            value: gfx.topMargin * 100,
            min: 0, max: 20, step: 1, suffix: '%', width: 100,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setTopMargin(v / 100),
          ),
        ),
        SettingRow(
          label: 'Bot Margin',
          child: SpinnerInput(
            value: gfx.botMargin * 100,
            min: 0, max: 20, step: 1, suffix: '%', width: 100,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setBotMargin(v / 100),
          ),
        ),
        SettingRow(
          label: 'Heads Up Custom Y',
          child: SpinnerInput(
            value: gfx.headsUpCustomY * 100,
            min: 0, max: 100, step: 5, suffix: '%', width: 100,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setHeadsUpCustomY(v / 100),
          ),
        ),
      ],
    );
  }
}
