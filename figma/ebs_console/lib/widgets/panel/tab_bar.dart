import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../theme/ebs_colors.dart';
import '../../providers/tab_provider.dart';

class EbsTabBar extends ConsumerWidget {
  const EbsTabBar({super.key});

  static const _tabs = ['Sources', 'Outputs', 'GFX', 'System'];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeTab = ref.watch(activeTabProvider);

    return ClipRect(
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
        child: Container(
          height: EbsColors.tabBarHeight,
          decoration: BoxDecoration(
            color: EbsColors.glassBg,
            border: const Border(
              top: BorderSide(color: EbsColors.glassBorder),
              bottom: BorderSide(color: EbsColors.glassBorder),
            ),
          ),
          child: Row(
            children: [
              for (int i = 0; i < _tabs.length; i++)
                _TabItem(
                  label: _tabs[i],
                  isActive: i == activeTab,
                  onTap: () =>
                      ref.read(activeTabProvider.notifier).state = i,
                ),
              const Spacer(),
            ],
          ),
        ),
      ),
    );
  }
}

class _TabItem extends StatefulWidget {
  final String label;
  final bool isActive;
  final VoidCallback onTap;

  const _TabItem({
    required this.label,
    required this.isActive,
    required this.onTap,
  });

  @override
  State<_TabItem> createState() => _TabItemState();
}

class _TabItemState extends State<_TabItem> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    final isActive = widget.isActive;
    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          curve: Curves.easeOut,
          padding: const EdgeInsets.symmetric(horizontal: 20),
          decoration: BoxDecoration(
            color: isActive
                ? EbsColors.accentGold.withValues(alpha: 0.06)
                : _hovered
                    ? Colors.white.withValues(alpha: 0.03)
                    : Colors.transparent,
            border: Border(
              bottom: BorderSide(
                color: isActive ? EbsColors.accentGold : Colors.transparent,
                width: 2,
              ),
            ),
            boxShadow: isActive
                ? [
                    BoxShadow(
                      color: EbsColors.accentGold.withValues(alpha: 0.18),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ]
                : null,
          ),
          alignment: Alignment.center,
          child: Text(
            widget.label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
              letterSpacing: isActive ? 0.6 : 0.4,
              color: isActive
                  ? EbsColors.accentGold
                  : _hovered
                      ? EbsColors.textPrimary
                      : EbsColors.textSecondary,
            ),
          ),
        ),
      ),
    );
  }
}
