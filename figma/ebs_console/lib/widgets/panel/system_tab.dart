import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/ebs_colors.dart';
import '../../providers/system_state_provider.dart';
import '../common/setting_row.dart';
import '../common/ebs_toggle.dart';
import '../common/ebs_button.dart';
import '../common/ebs_dropdown.dart';
import '../common/rfid_antenna_card.dart';
import '../common/diagnostic_panel.dart';
import '../common/section_title.dart';

class SystemTab extends ConsumerWidget {
  const SystemTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sys = ref.watch(systemStateProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(EbsColors.spacingMd),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // RFID 3 ANTENNAS
          const SectionTitle('RFID Antennas', padding: EdgeInsets.zero),
          const SizedBox(height: 8),
          Row(
            children: [
              for (int i = 0; i < sys.antennas.length; i++) ...[
                if (i > 0) const SizedBox(width: 8),
                Expanded(child: RfidAntennaCard(antenna: sys.antennas[i])),
              ],
            ],
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // TABLE
          const SectionTitle('Table', padding: EdgeInsets.zero),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Table Name',
            child: _TextInput(value: 'Final Table', width: 130),
          ),
          SettingRow(
            label: 'Table Password',
            child: _TextInput(value: '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022', width: 130),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: EbsButton(text: 'RESET', small: true)),
              const SizedBox(width: 8),
              Expanded(child: EbsButton(text: 'CALIBRATE', small: true)),
              const SizedBox(width: 8),
              Expanded(child: EbsButton(text: 'UPDATE', small: true)),
            ],
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // ACTION TRACKER
          const SectionTitle('Action Tracker', padding: EdgeInsets.zero),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Allow AT Access',
            child: EbsToggle(
              value: sys.atConnected,
              onChanged: (_) => ref.read(systemStateProvider.notifier).toggleAtConnected(),
            ),
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // DIAGNOSTICS
          const SectionTitle('Diagnostics', padding: EdgeInsets.zero),
          const SizedBox(height: 8),
          DiagnosticPanel(diagnostics: sys.diagnostics),
          const SizedBox(height: 12),
          SettingRow(
            label: 'Log Level',
            child: EbsDropdown(
              value: 'INFO',
              items: const ['DEBUG', 'INFO', 'WARN', 'ERROR'],
              width: 90,
            ),
          ),
          SettingRow(
            label: 'Export Folder',
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'C:\\EBS\\exports\\',
                  style: GoogleFonts.jetBrainsMono(fontSize: 11, color: EbsColors.textMuted),
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(width: 6),
                EbsButton(text: 'BROWSE', small: true),
              ],
            ),
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // CONFIG
          const SectionTitle('Config', padding: EdgeInsets.zero),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: EbsButton(text: 'EXPORT CONFIG')),
              const SizedBox(width: 8),
              Expanded(child: EbsButton(text: 'IMPORT CONFIG')),
            ],
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // STARTUP
          const SectionTitle('Startup', padding: EdgeInsets.zero),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Auto Start',
            child: EbsToggle(value: false),
          ),
          SettingRow(
            label: 'Auto Connect',
            child: EbsToggle(value: true),
          ),
          SettingRow(
            label: 'Default Theme',
            child: EbsDropdown(
              value: 'Dark',
              items: const ['Dark', 'Light'],
              width: 80,
            ),
          ),
        ],
      ),
    );
  }
}

class _TextInput extends StatelessWidget {
  final String value;
  final double width;
  const _TextInput({required this.value, required this.width});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.05),
        border: Border.all(color: EbsColors.glassBorder),
        borderRadius: BorderRadius.circular(EbsColors.borderRadiusSm),
      ),
      child: Text(
        value,
        style: const TextStyle(fontSize: 12, color: EbsColors.textPrimary),
      ),
    );
  }
}
