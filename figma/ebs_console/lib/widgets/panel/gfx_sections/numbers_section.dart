import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../theme/ebs_colors.dart';
import '../../../providers/gfx_settings_provider.dart';
import '../../common/precision_dropdown.dart';
import '../../common/ebs_dropdown.dart';
import '../../common/ebs_toggle.dart';
import '../../common/setting_row.dart';

class NumbersSection extends ConsumerWidget {
  const NumbersSection({super.key});

  static const _precisionAreas = [
    'Player Stack', 'Player Action', 'Pot', 'Blinds',
    'Leaderboard', 'Chipcounts', 'Ticker', 'Twitch Bot',
  ];

  static const _displayAreas = ['Chipcounts', 'Pot', 'Bets'];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gfx = ref.watch(gfxSettingsProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Chipcount Precision
        const Text(
          'CHIPCOUNT PRECISION',
          style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700, letterSpacing: 0.8, color: EbsColors.textMuted),
        ),
        const SizedBox(height: 6),
        for (final area in _precisionAreas) ...[
          PrecisionDropdown(
            label: area,
            value: gfx.chipPrecision[area] ?? 'Smart',
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setChipPrecision(area, v),
          ),
          const SizedBox(height: 4),
        ],
        const SizedBox(height: EbsColors.spacingSm),

        // Display Mode
        const Text(
          'DISPLAY MODE',
          style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700, letterSpacing: 0.8, color: EbsColors.textMuted),
        ),
        const SizedBox(height: 6),
        for (final area in _displayAreas) ...[
          PrecisionDropdown(
            label: area,
            value: gfx.displayMode[area] ?? 'Amount',
            items: const ['Amount', 'BB Multiple', 'Both'],
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setDisplayMode(area, v),
          ),
          const SizedBox(height: 4),
        ],
        const SizedBox(height: EbsColors.spacingSm),

        // Currency
        const Text(
          'CURRENCY',
          style: TextStyle(fontSize: 9, fontWeight: FontWeight.w700, letterSpacing: 0.8, color: EbsColors.textMuted),
        ),
        const SizedBox(height: 6),
        SettingRow(
          label: 'Symbol',
          child: EbsDropdown(
            value: gfx.currencySymbol,
            items: const ['\$', 'EUR', 'GBP', 'JPY', 'KRW'],
            width: 80,
            onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setCurrencySymbol(v),
          ),
        ),
        SettingRow(
          label: 'Trailing Zeros',
          child: EbsToggle(
            value: gfx.trailingZeros,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleTrailingZeros(),
          ),
        ),
        SettingRow(
          label: 'Divide by 100',
          child: EbsToggle(
            value: gfx.divideBy100,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleDivideBy100(),
          ),
        ),
      ],
    );
  }
}
