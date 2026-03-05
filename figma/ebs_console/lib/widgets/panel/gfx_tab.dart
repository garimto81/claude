import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../providers/tab_provider.dart';
import '../common/collapsible_section.dart';
import 'gfx_sections/layout_section.dart';
import 'gfx_sections/card_player_section.dart';
import 'gfx_sections/animation_section.dart';
import 'gfx_sections/numbers_section.dart';
import 'gfx_sections/rules_section.dart';
import 'gfx_sections/branding_section.dart';

class GfxTab extends ConsumerWidget {
  const GfxTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return SingleChildScrollView(
      child: Column(
        children: [
          CollapsibleSection(
            title: 'Layout',
            isExpanded: ref.watch(gfxLayoutExpandedProvider),
            onToggle: () => ref.read(gfxLayoutExpandedProvider.notifier).update((s) => !s),
            child: const LayoutSection(),
          ),
          CollapsibleSection(
            title: 'Card & Player',
            isExpanded: ref.watch(gfxCardPlayerExpandedProvider),
            onToggle: () => ref.read(gfxCardPlayerExpandedProvider.notifier).update((s) => !s),
            child: const CardPlayerSection(),
          ),
          CollapsibleSection(
            title: 'Animation',
            isExpanded: ref.watch(gfxAnimationExpandedProvider),
            onToggle: () => ref.read(gfxAnimationExpandedProvider.notifier).update((s) => !s),
            child: const AnimationSection(),
          ),
          CollapsibleSection(
            title: 'Numbers',
            isExpanded: ref.watch(gfxNumbersExpandedProvider),
            onToggle: () => ref.read(gfxNumbersExpandedProvider.notifier).update((s) => !s),
            child: const NumbersSection(),
          ),
          CollapsibleSection(
            title: 'Rules',
            isExpanded: ref.watch(gfxRulesExpandedProvider),
            onToggle: () => ref.read(gfxRulesExpandedProvider.notifier).update((s) => !s),
            child: const RulesSection(),
          ),
          CollapsibleSection(
            title: 'Branding',
            isExpanded: ref.watch(gfxBrandingExpandedProvider),
            onToggle: () => ref.read(gfxBrandingExpandedProvider.notifier).update((s) => !s),
            child: const BrandingSection(),
          ),
        ],
      ),
    );
  }
}
