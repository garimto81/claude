import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../theme/ebs_colors.dart';
import '../../../providers/gfx_settings_provider.dart';
import '../../common/ebs_toggle.dart';
import '../../common/ebs_dropdown.dart';
import '../../common/spinner_input.dart';
import '../../common/setting_row.dart';

class RulesSection extends ConsumerWidget {
  const RulesSection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gfx = ref.watch(gfxSettingsProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Game Rules
        const Text(
          'GAME RULES',
          style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700, letterSpacing: 0.8, color: EbsColors.textMuted),
        ),
        const SizedBox(height: 6),
        SettingRow(
          label: 'Move Button (Bomb Pot)',
          child: EbsToggle(
            value: gfx.moveButtonAfterBombPot,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleMoveButton(),
          ),
        ),
        SettingRow(
          label: 'Limit Raises',
          child: SpinnerInput(
            value: gfx.limitRaises.toDouble(),
            min: 1, max: 10, step: 1, width: 80,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setLimitRaises(v.toInt()),
          ),
        ),
        SettingRow(
          label: 'Straddle',
          child: EbsToggle(
            value: gfx.straddleEnabled,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleStraddle(),
          ),
        ),
        SettingRow(
          label: 'Sleeper',
          child: EbsToggle(
            value: gfx.sleeperEnabled,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleSleeper(),
          ),
        ),
        const SizedBox(height: EbsColors.spacingSm),

        // Display
        const Text(
          'DISPLAY',
          style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700, letterSpacing: 0.8, color: EbsColors.textMuted),
        ),
        const SizedBox(height: 6),
        SettingRow(
          label: 'Equity Show Timing',
          child: EbsDropdown(
            value: gfx.equityShowTiming,
            items: const ['After All-In', 'Always', 'Never'],
            width: 120,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setEquityShowTiming(v),
          ),
        ),
        SettingRow(
          label: 'Player Ordering',
          child: EbsDropdown(
            value: gfx.playerOrdering,
            items: const ['Clockwise', 'By Stack', 'By Seat'],
            width: 120,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setPlayerOrdering(v),
          ),
        ),
        SettingRow(
          label: 'Winning Hand Highlight',
          child: EbsToggle(
            value: gfx.winningHandHighlight,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleWinningHandHighlight(),
          ),
        ),
        SettingRow(
          label: 'Add Seat #',
          child: EbsToggle(
            value: gfx.addSeatNumber,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleAddSeatNumber(),
          ),
        ),
        SettingRow(
          label: 'Show Eliminated',
          child: EbsToggle(
            value: gfx.showEliminated,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleShowEliminated(),
          ),
        ),
        SettingRow(
          label: 'Allow Rabbit Hunting',
          child: EbsToggle(
            value: gfx.allowRabbitHunting,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleRabbitHunting(),
          ),
        ),
        SettingRow(
          label: 'Display Side Pot',
          child: EbsToggle(
            value: gfx.displaySidePot,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleDisplaySidePot(),
          ),
        ),
        const SizedBox(height: EbsColors.spacingSm),

        // Leaderboard
        const Text(
          'LEADERBOARD',
          style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700, letterSpacing: 0.8, color: EbsColors.textMuted),
        ),
        const SizedBox(height: 6),
        SettingRow(
          label: 'Knockout Rank',
          child: EbsToggle(
            value: gfx.knockoutRank,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleKnockoutRank(),
          ),
        ),
        SettingRow(
          label: 'Chipcount %',
          child: EbsToggle(
            value: gfx.chipcountPercent,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleChipcountPercent(),
          ),
        ),
        SettingRow(
          label: 'Show Eliminated',
          child: EbsToggle(
            value: gfx.showEliminatedLeaderboard,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleShowEliminatedLeaderboard(),
          ),
        ),
        SettingRow(
          label: 'Cumulative Score',
          child: EbsToggle(
            value: gfx.cumulativeScore,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleCumulativeScore(),
          ),
        ),
        SettingRow(
          label: 'Hide on Hand',
          child: EbsToggle(
            value: gfx.hideOnHand,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleHideOnHand(),
          ),
        ),
        SettingRow(
          label: 'Max BB Display',
          child: SpinnerInput(
            value: gfx.maxBBDisplay.toDouble(),
            min: 100, max: 9999, step: 100, width: 100,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setMaxBBDisplay(v.toInt()),
          ),
        ),
        const SizedBox(height: EbsColors.spacingSm),

        // Outs/Equity
        const Text(
          'OUTS / EQUITY',
          style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700, letterSpacing: 0.8, color: EbsColors.textMuted),
        ),
        const SizedBox(height: 6),
        SettingRow(
          label: 'Show Outs Position',
          child: EbsDropdown(
            value: gfx.showOutsPosition,
            items: const ['Above', 'Below', 'Hidden'],
            width: 100,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setShowOutsPosition(v),
          ),
        ),
        SettingRow(
          label: 'True Outs',
          child: EbsToggle(
            value: gfx.trueOuts,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleTrueOuts(),
          ),
        ),
        SettingRow(
          label: 'Score Strip Mode',
          child: EbsDropdown(
            value: gfx.scoreStripMode,
            items: const ['Compact', 'Full', 'Hidden'],
            width: 100,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setScoreStripMode(v),
          ),
        ),
      ],
    );
  }
}
