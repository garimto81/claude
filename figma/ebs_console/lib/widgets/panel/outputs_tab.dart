import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../theme/ebs_colors.dart';
import '../../providers/outputs_provider.dart';
import '../common/setting_row.dart';
import '../common/ebs_toggle.dart';
import '../common/ebs_dropdown.dart';
import '../common/color_swatch_widget.dart';
import '../common/section_title.dart';

class OutputsTab extends ConsumerWidget {
  const OutputsTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final out = ref.watch(outputsSettingsProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(EbsColors.spacingMd),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // RESOLUTION
          const SectionTitle('Resolution', padding: EdgeInsets.zero),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Video Size',
            child: EbsDropdown(
              value: out.videoSize,
              items: const ['1920x1080', '1280x720', '3840x2160'],
              width: 140,
              onChanged: (v) => ref.read(outputsSettingsProvider.notifier).setVideoSize(v),
            ),
          ),
          SettingRow(
            label: '9\u00D716 Vertical',
            child: EbsToggle(
              value: out.verticalMode,
              onChanged: (_) => ref.read(outputsSettingsProvider.notifier).toggleVerticalMode(),
            ),
          ),
          SettingRow(
            label: 'Frame Rate',
            child: EbsDropdown(
              value: '${out.frameRate}fps',
              items: const ['60fps', '30fps', '50fps'],
              width: 100,
              onChanged: (v) => ref.read(outputsSettingsProvider.notifier)
                  .setFrameRate(int.parse(v.replaceAll('fps', ''))),
            ),
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // LIVE PIPELINE
          const SectionTitle('Live Pipeline', padding: EdgeInsets.zero),
          const SizedBox(height: 8),
          SettingRow(
            label: 'NDI Output',
            child: EbsDropdown(
              value: out.ndiOutput,
              items: const ['Disabled', 'NDI 1', 'NDI 2'],
              width: 120,
              onChanged: (v) => ref.read(outputsSettingsProvider.notifier).setNdiOutput(v),
            ),
          ),
          SettingRow(
            label: 'DeckLink',
            child: EbsDropdown(
              value: out.deckLinkOutput,
              items: const ['Disabled', 'DeckLink 4K Extreme', 'DeckLink Mini Monitor'],
              width: 160,
              onChanged: (v) => ref.read(outputsSettingsProvider.notifier).setDeckLinkOutput(v),
            ),
          ),
          SettingRow(
            label: 'Audio Preview',
            child: EbsDropdown(
              value: out.audioPreview,
              items: const ['Default', 'Monitor', 'System Default'],
              width: 130,
              onChanged: (v) => ref.read(outputsSettingsProvider.notifier).setAudioPreview(v),
            ),
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // FILL & KEY
          const SectionTitle('Fill & Key', padding: EdgeInsets.zero),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Key & Fill',
            child: EbsToggle(
              value: out.fillAndKeyEnabled,
              onChanged: (_) => ref.read(outputsSettingsProvider.notifier).toggleFillAndKey(),
            ),
          ),
          SettingRow(
            label: 'Key Color',
            child: const ColorSwatchWidget(
              color: Color(0xFF000000),
              hexLabel: '#FF000000',
            ),
          ),
          const SizedBox(height: 12),
          // Fill/Key preview
          Row(
            children: [
              Expanded(child: _FkPreviewBox(label: 'FILL', port: 'Port 1', color: Colors.white.withValues(alpha: 0.06))),
              const SizedBox(width: 8),
              Expanded(child: _FkPreviewBox(label: 'KEY', port: 'Port 2', color: Colors.black)),
            ],
          ),
          const SizedBox(height: EbsColors.spacingLg),

          // COLOR SPACE
          const SectionTitle('Color Space', padding: EdgeInsets.zero),
          const SizedBox(height: 8),
          SettingRow(
            label: 'Color Space',
            child: EbsDropdown(
              value: out.colorSpace,
              items: const ['BT.709', 'BT.2020'],
              width: 100,
              onChanged: (v) => ref.read(outputsSettingsProvider.notifier).setColorSpace(v),
            ),
          ),
          SettingRow(
            label: 'Bit Depth',
            child: EbsDropdown(
              value: out.bitDepth,
              items: const ['8-bit', '10-bit'],
              width: 100,
              onChanged: (v) => ref.read(outputsSettingsProvider.notifier).setBitDepth(v),
            ),
          ),
        ],
      ),
    );
  }
}

class _FkPreviewBox extends StatelessWidget {
  final String label;
  final String port;
  final Color color;
  const _FkPreviewBox({required this.label, required this.port, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        AspectRatio(
          aspectRatio: 16 / 9,
          child: Container(
            decoration: BoxDecoration(
              color: color,
              border: Border.all(color: EbsColors.glassBorder),
              borderRadius: BorderRadius.circular(3),
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(fontSize: 9, fontWeight: FontWeight.w700, letterSpacing: 0.72, color: EbsColors.textMuted)),
        Text(port, style: const TextStyle(fontSize: 10, color: EbsColors.textSecondary)),
      ],
    );
  }
}
