import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/ebs_colors.dart';
import '../../providers/sources_provider.dart';
import '../common/setting_row.dart';
import '../common/ebs_toggle.dart';
import '../common/ebs_dropdown.dart';
import '../common/ebs_badge.dart';
import '../common/ebs_button.dart';
import '../common/status_indicator.dart';
import '../common/spinner_input.dart';
import '../common/color_swatch_widget.dart';
import '../common/segment_toggle.dart';
import '../common/section_title.dart';

class SourcesTab extends ConsumerWidget {
  const SourcesTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final src = ref.watch(sourcesSettingsProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(EbsColors.spacingSm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // VIDEO SOURCES TABLE (7 columns)
          const SectionTitle('Video Sources'),
          const SizedBox(height: 8),
          const _SourceTable(),
          const SizedBox(height: EbsColors.spacingLg),

          // BOARD SYNC
          const SectionTitle('Board Sync'),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Offset X',
            child: SpinnerInput(
              value: src.boardSyncOffsetX,
              min: -50, max: 50, step: 1,
              suffix: 'px',
              width: 110,
              onChanged: (v) => ref.read(sourcesSettingsProvider.notifier).setBoardSyncOffsetX(v),
            ),
          ),
          SettingRow(
            label: 'Offset Y',
            child: SpinnerInput(
              value: src.boardSyncOffsetY,
              min: -50, max: 50, step: 1,
              suffix: 'px',
              width: 110,
              onChanged: (v) => ref.read(sourcesSettingsProvider.notifier).setBoardSyncOffsetY(v),
            ),
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // CHROMA KEY
          const SectionTitle('Chroma Key'),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Enable',
            child: EbsToggle(
              value: src.chromaKeyEnabled,
              onChanged: (_) => ref.read(sourcesSettingsProvider.notifier).toggleChromaKey(),
            ),
          ),
          SettingRow(
            label: 'Background Color',
            child: const ColorSwatchWidget(color: Color(0xFF0000FF), hexLabel: '#0000FF'),
          ),
          SettingRow(
            label: 'Intensity',
            child: SpinnerInput(
              value: src.chromaKeyIntensity,
              min: 0, max: 1, step: 0.05,
              width: 100,
              onChanged: (v) => ref.read(sourcesSettingsProvider.notifier).setChromaKeyIntensity(v),
            ),
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // CAMERA MODE
          const SectionTitle('Camera Mode'),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Mode',
            child: SegmentToggle(
              labels: const ['STATIC', 'DYNAMIC'],
              selectedIndex: src.cameraMode == 'STATIC' ? 0 : 1,
              onChanged: (i) => ref.read(sourcesSettingsProvider.notifier)
                  .setCameraMode(i == 0 ? 'STATIC' : 'DYNAMIC'),
            ),
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // ATEM CONTROL
          const SectionTitle('ATEM Control'),
          const SizedBox(height: 8),
          SettingRow(
            label: 'ATEM IP',
            child: Container(
              width: 130,
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.05),
                border: Border.all(color: EbsColors.glassBorder),
                borderRadius: BorderRadius.circular(EbsColors.borderRadiusSm),
              ),
              child: Text(
                src.atemIp ?? 'Not connected',
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 12,
                  color: src.atemIp != null ? EbsColors.textPrimary : EbsColors.textMuted,
                ),
              ),
            ),
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // CROSSFADE
          const SectionTitle('Crossfade'),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Duration',
            child: SpinnerInput(
              value: src.crossfadeDuration,
              min: 0, max: 5, step: 0.1,
              suffix: 's',
              width: 100,
              onChanged: (v) => ref.read(sourcesSettingsProvider.notifier).setCrossfadeDuration(v),
            ),
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // AUDIO INPUT
          const SectionTitle('Audio Input'),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Input',
            child: EbsDropdown(
              value: src.audioInput,
              items: const ['Default', 'HDMI 1', 'USB Audio'],
              width: 130,
              onChanged: (v) => ref.read(sourcesSettingsProvider.notifier).setAudioInput(v),
            ),
          ),
        ],
      ),
    );
  }
}

class _SourceTable extends StatelessWidget {
  const _SourceTable();

  @override
  Widget build(BuildContext context) {
    final headerStyle = TextStyle(
      fontSize: 9,
      fontWeight: FontWeight.w700,
      letterSpacing: 0.63,
      color: EbsColors.textMuted,
    );

    final sources = [
      ('1', 'L', 'Camera 1', '1080p60', '60Hz', 'Active', true),
      ('2', 'R', 'Camera 2', '720p30', '30Hz', 'Inactive', false),
      ('3', '', 'NDI Input 1', '', '', 'No Signal', false),
      ('4', '', 'NDI Input 2', '', '', 'No Signal', false),
    ];

    return Table(
      columnWidths: const {
        0: FixedColumnWidth(20),
        1: FixedColumnWidth(20),
        2: FlexColumnWidth(2),
        3: FixedColumnWidth(65),
        4: FixedColumnWidth(40),
        5: FlexColumnWidth(1),
        6: FixedColumnWidth(50),
      },
      defaultVerticalAlignment: TableCellVerticalAlignment.middle,
      children: [
        TableRow(
          decoration: BoxDecoration(
            color: EbsColors.bgSecondary,
            border: Border(bottom: BorderSide(color: EbsColors.glassBorder)),
          ),
          children: [
            _cell(Text('L', style: headerStyle), pad: 5),
            _cell(Text('R', style: headerStyle), pad: 5),
            _cell(Text('SOURCE', style: headerStyle), pad: 5),
            _cell(Text('FORMAT', style: headerStyle), pad: 5),
            _cell(Text('CYCLE', style: headerStyle), pad: 5),
            _cell(Text('STATUS', style: headerStyle), pad: 5),
            _cell(Text('', style: headerStyle), pad: 5),
          ],
        ),
        for (final s in sources)
          TableRow(
            children: [
              _cell(
                s.$7
                    ? const StatusIndicator(type: IndicatorType.active, size: 7)
                    : const SizedBox(width: 7),
                pad: 6,
              ),
              _cell(
                Text(s.$2, style: TextStyle(fontSize: 10, color: EbsColors.textMuted)),
                pad: 6,
              ),
              _cell(
                Text(s.$3, style: TextStyle(
                  fontSize: 11,
                  fontWeight: s.$7 ? FontWeight.w700 : FontWeight.w400,
                  color: s.$7 ? EbsColors.textPrimary : EbsColors.textSecondary,
                )),
                pad: 6,
              ),
              _cell(
                Text(
                  s.$4.isEmpty ? '\u2014' : s.$4,
                  style: GoogleFonts.jetBrainsMono(
                    fontSize: 11,
                    color: s.$4.isNotEmpty ? EbsColors.textSecondary : EbsColors.textMuted,
                  ),
                ),
                pad: 6,
              ),
              _cell(
                Text(
                  s.$5.isEmpty ? '\u2014' : s.$5,
                  style: GoogleFonts.jetBrainsMono(fontSize: 10, color: EbsColors.textMuted),
                ),
                pad: 6,
              ),
              _cell(
                EbsBadge(
                  text: s.$6,
                  variant: switch (s.$6) {
                    'Active' => BadgeVariant.success,
                    'Inactive' => BadgeVariant.muted,
                    _ => BadgeVariant.danger,
                  },
                ),
                pad: 6,
              ),
              _cell(
                EbsButton(
                  text: s.$6 == 'No Signal' ? 'LINK' : 'EDIT',
                  small: true,
                ),
                pad: 6,
              ),
            ],
          ),
      ],
    );
  }

  Widget _cell(Widget child, {double pad = 6}) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: pad, horizontal: 4),
      child: child,
    );
  }
}
