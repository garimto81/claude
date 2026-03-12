import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../providers/gfx_settings_provider.dart';
import '../../common/ebs_dropdown.dart';
import '../../common/ebs_toggle.dart';
import '../../common/spinner_input.dart';
import '../../common/setting_row.dart';

class AnimationSection extends ConsumerWidget {
  const AnimationSection({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final gfx = ref.watch(gfxSettingsProvider);

    return Column(
      children: [
        SettingRow(
          label: 'Transition In',
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              EbsDropdown(
                value: gfx.transitionIn,
                items: const ['Fade', 'Slide', 'Pop', 'Expand'],
                width: 90,
                onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setTransitionIn(v),
              ),
              const SizedBox(width: 4),
              SpinnerInput(
                value: gfx.transitionInTime,
                min: 0.1, max: 5.0, step: 0.1, suffix: 's', width: 80,
                onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setTransitionInTime(v),
              ),
            ],
          ),
        ),
        SettingRow(
          label: 'Transition Out',
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              EbsDropdown(
                value: gfx.transitionOut,
                items: const ['Fade', 'Slide', 'Pop', 'Expand'],
                width: 90,
                onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setTransitionOut(v),
              ),
              const SizedBox(width: 4),
              SpinnerInput(
                value: gfx.transitionOutTime,
                min: 0.1, max: 5.0, step: 0.1, suffix: 's', width: 80,
                onChanged: (v) => ref.read(gfxSettingsProvider.notifier).setTransitionOutTime(v),
              ),
            ],
          ),
        ),
        SettingRow(
          label: 'Indent Action Player',
          child: EbsToggle(
            value: gfx.indentActionPlayer,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleIndentActionPlayer(),
          ),
        ),
        SettingRow(
          label: 'Bounce Action Player',
          child: EbsToggle(
            value: gfx.bounceActionPlayer,
            onChanged: (_) => ref.read(gfxSettingsProvider.notifier).toggleBounceActionPlayer(),
          ),
        ),
      ],
    );
  }
}
