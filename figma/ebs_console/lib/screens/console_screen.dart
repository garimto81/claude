import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/ebs_colors.dart';
import '../providers/tab_provider.dart';
import '../widgets/header/app_header.dart';
import '../widgets/preview/live_preview.dart';
import '../widgets/panel/tab_bar.dart';
import '../widgets/panel/sources_tab.dart';
import '../widgets/panel/outputs_tab.dart';
import '../widgets/panel/gfx_tab.dart';
import '../widgets/panel/system_tab.dart';
import 'command_palette.dart';

class ConsoleScreen extends ConsumerWidget {
  const ConsoleScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final showPalette = ref.watch(commandPaletteVisibleProvider);
    final activeTab = ref.watch(activeTabProvider);

    return Scaffold(
      body: CallbackShortcuts(
        bindings: {
          const SingleActivator(LogicalKeyboardKey.keyK, meta: true): () {
            ref.read(commandPaletteVisibleProvider.notifier).state = true;
          },
          const SingleActivator(LogicalKeyboardKey.keyK, control: true): () {
            ref.read(commandPaletteVisibleProvider.notifier).state = true;
          },
          const SingleActivator(LogicalKeyboardKey.digit1, meta: true): () {
            ref.read(activeTabProvider.notifier).state = 0;
          },
          const SingleActivator(LogicalKeyboardKey.digit1, control: true): () {
            ref.read(activeTabProvider.notifier).state = 0;
          },
          const SingleActivator(LogicalKeyboardKey.digit2, meta: true): () {
            ref.read(activeTabProvider.notifier).state = 1;
          },
          const SingleActivator(LogicalKeyboardKey.digit2, control: true): () {
            ref.read(activeTabProvider.notifier).state = 1;
          },
          const SingleActivator(LogicalKeyboardKey.digit3, meta: true): () {
            ref.read(activeTabProvider.notifier).state = 2;
          },
          const SingleActivator(LogicalKeyboardKey.digit3, control: true): () {
            ref.read(activeTabProvider.notifier).state = 2;
          },
          const SingleActivator(LogicalKeyboardKey.digit4, meta: true): () {
            ref.read(activeTabProvider.notifier).state = 3;
          },
          const SingleActivator(LogicalKeyboardKey.digit4, control: true): () {
            ref.read(activeTabProvider.notifier).state = 3;
          },
          const SingleActivator(LogicalKeyboardKey.keyR, meta: true): () {},
          const SingleActivator(LogicalKeyboardKey.keyR, control: true): () {},
          const SingleActivator(LogicalKeyboardKey.keyL, meta: true): () {},
          const SingleActivator(LogicalKeyboardKey.keyL, control: true): () {},
          const SingleActivator(LogicalKeyboardKey.keyH, meta: true): () {},
          const SingleActivator(LogicalKeyboardKey.keyH, control: true): () {},
          const SingleActivator(
            LogicalKeyboardKey.slash,
            control: true,
            shift: true,
          ): () {
            ref
                .read(shortcutGuideVisibleProvider.notifier)
                .update((s) => !s);
          },
          const SingleActivator(LogicalKeyboardKey.escape): () {
            ref.read(commandPaletteVisibleProvider.notifier).state = false;
            ref.read(shortcutGuideVisibleProvider.notifier).state = false;
          },
        },
        child: Focus(
          autofocus: true,
          child: Stack(
            children: [
              Column(
                children: [
                  const AppHeader(),
                  const Expanded(child: LivePreview()),
                  const EbsTabBar(),
                  SizedBox(
                    height: EbsColors.tabContentHeight,
                    child: _TabContent(activeTab: activeTab),
                  ),
                ],
              ),
              if (showPalette) const CommandPalette(),
            ],
          ),
        ),
      ),
    );
  }
}

class _TabContent extends StatelessWidget {
  final int activeTab;
  const _TabContent({required this.activeTab});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: EbsColors.bgTertiary,
        border: Border(
          top: BorderSide(
            color: Colors.white.withValues(alpha: 0.04),
          ),
        ),
      ),
      child: AnimatedSwitcher(
        duration: const Duration(milliseconds: 200),
        transitionBuilder: (child, animation) {
          return FadeTransition(opacity: animation, child: child);
        },
        child: IndexedStack(
          key: ValueKey<int>(activeTab),
          index: activeTab,
          children: const [SourcesTab(), OutputsTab(), GfxTab(), SystemTab()],
        ),
      ),
    );
  }
}
