import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../providers/gfx_settings_provider.dart';
import '../../common/ebs_dropdown.dart';
import '../../common/ebs_toggle.dart';
import '../../common/spinner_input.dart';
import '../../common/setting_row.dart';

class CardPlayerSection extends ConsumerWidget {
  const CardPlayerSection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gfx = ref.watch(gfxSettingsProvider);

    return Column(
      children: [
        SettingRow(
          label: 'Reveal Players',
          child: EbsDropdown(
            value: gfx.revealPlayers,
            items: const ['Immediate', 'Delayed'],
            width: 130,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setRevealPlayers(v),
          ),
        ),
        SettingRow(
          label: 'Show Fold',
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              EbsDropdown(
                value: gfx.showFold,
                items: const ['Immediate', 'Action On', 'After Bet', 'Action On+Next'],
                width: 120,
                onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setShowFold(v),
              ),
              const SizedBox(width: 4),
              SpinnerInput(
                value: gfx.foldDelayTime,
                min: 0, max: 10, step: 0.5, suffix: 's', width: 80,
                onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setFoldDelayTime(v),
              ),
            ],
          ),
        ),
        SettingRow(
          label: 'Reveal Cards',
          child: EbsDropdown(
            value: gfx.revealCards,
            items: const [
              'Immediate', 'On Action', 'After Bet',
              'After River', 'Showdown-Cash', 'Showdown-Tourney',
            ],
            width: 150,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setRevealCards(v),
          ),
        ),
        SettingRow(
          label: 'Heads Up History',
          child: EbsToggle(
            value: gfx.showHeadsUpHistory,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleShowHeadsUpHistory(),
          ),
        ),
        SettingRow(
          label: 'Action Clock',
          child: SpinnerInput(
            value: gfx.actionClockThreshold,
            min: 5, max: 60, step: 5, suffix: 's', width: 100,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setActionClockThreshold(v),
          ),
        ),
      ],
    );
  }
}
