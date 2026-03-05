import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/ebs_colors.dart';
import '../../providers/game_state_provider.dart';
import '../../providers/system_state_provider.dart';
import '../../providers/tab_provider.dart';
import '../common/status_indicator.dart';
import '../common/ebs_button.dart';

class AppHeader extends ConsumerWidget {
  const AppHeader({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final game = ref.watch(gameStateProvider);
    final system = ref.watch(systemStateProvider);
    final tables = ref.watch(tableListProvider);

    return ClipRect(
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
        child: Container(
          height: EbsColors.headerHeight,
          padding: const EdgeInsets.symmetric(horizontal: EbsColors.spacingMd),
          decoration: BoxDecoration(
            color: EbsColors.glassBg,
            border: const Border(
              bottom: BorderSide(color: EbsColors.glassBorder, width: 1),
            ),
            boxShadow: [
              BoxShadow(
                color: EbsColors.glassShadow,
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            children: [
              // Left: Logo + Table dropdown
              const Text(
                'E B S',
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.2,
                  color: EbsColors.accentGold,
                  shadows: [
                    Shadow(
                      color: Color(0x66D4AF37),
                      blurRadius: 8,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: EbsColors.spacingSm),
              Container(width: 1, height: 20, color: EbsColors.glassBorder),
              const SizedBox(width: EbsColors.spacingSm),
              // Table dropdown
              DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  value: game.tableName,
                  isDense: true,
                  dropdownColor: EbsColors.bgSecondary,
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    color: EbsColors.textPrimary,
                  ),
                  icon: const Icon(
                    Icons.expand_more,
                    size: 14,
                    color: EbsColors.textMuted,
                  ),
                  items: tables
                      .map(
                        (t) => DropdownMenuItem(
                          value: t,
                          child: Padding(
                            padding: const EdgeInsets.symmetric(vertical: 2),
                            child: Text(t),
                          ),
                        ),
                      )
                      .toList(),
                  onChanged: (v) {
                    if (v != null) {
                      ref.read(gameStateProvider.notifier).updateTableName(v);
                    }
                  },
                ),
              ),

              const Spacer(),

              // Center: RFID + CPU + GPU indicators
              StatusIndicator(
                type: system.rfidConnected
                    ? IndicatorType.active
                    : IndicatorType.idle,
                size: 7,
              ),
              const SizedBox(width: 4),
              Text(
                'RFID',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.6,
                  color: system.rfidConnected
                      ? EbsColors.success
                      : EbsColors.textMuted,
                ),
              ),
              const SizedBox(width: EbsColors.spacingMd),
              const Text(
                'CPU',
                style: TextStyle(
                  fontSize: 10,
                  letterSpacing: 0.5,
                  color: EbsColors.textMuted,
                ),
              ),
              const SizedBox(width: 4),
              Text(
                '${(system.cpuUsage * 100).toInt()}%',
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 10,
                  color: EbsColors.textSecondary,
                  fontFeatures: const [FontFeature.tabularFigures()],
                ),
              ),
              const SizedBox(width: EbsColors.spacingSm),
              const Text(
                'GPU',
                style: TextStyle(
                  fontSize: 10,
                  letterSpacing: 0.5,
                  color: EbsColors.textMuted,
                ),
              ),
              const SizedBox(width: 4),
              Text(
                '${(system.gpuUsage * 100).toInt()}%',
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 10,
                  color: EbsColors.textSecondary,
                  fontFeatures: const [FontFeature.tabularFigures()],
                ),
              ),

              const Spacer(),

              // Right: Quick Actions
              EbsButton(text: 'Reset', small: true),
              const SizedBox(width: 4),
              EbsButton(text: 'Deck', small: true),
              const SizedBox(width: 4),
              EbsButton(text: 'AT', small: true),
              const SizedBox(width: 4),
              EbsButton(text: 'Hide', small: true),
              const SizedBox(width: EbsColors.spacingSm),
              // Cmd+K button
              GestureDetector(
                onTap: () {
                  ref
                      .read(commandPaletteVisibleProvider.notifier)
                      .state = true;
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.06),
                    border: Border.all(color: EbsColors.glassBorder),
                    borderRadius: BorderRadius.circular(EbsColors.borderRadiusSm),
                  ),
                  child: Text(
                    '\u2318K',
                    style: GoogleFonts.jetBrainsMono(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: EbsColors.textPrimary,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: EbsColors.spacingSm),
              // LIVE badge with neon glow
              _LiveBadge(),
            ],
          ),
        ),
      ),
    );
  }
}

class _LiveBadge extends StatefulWidget {
  @override
  State<_LiveBadge> createState() => _LiveBadgeState();
}

class _LiveBadgeState extends State<_LiveBadge>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _glow;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    _glow = Tween<double>(begin: 4.0, end: 12.0).animate(
      CurvedAnimation(parent: _ctrl, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _glow,
      builder: (_, child) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(
            color: EbsColors.danger.withValues(alpha: 0.15),
            border: Border.all(
              color: EbsColors.danger.withValues(alpha: 0.4),
            ),
            borderRadius: BorderRadius.circular(100),
            boxShadow: [
              BoxShadow(
                color: EbsColors.danger.withValues(alpha: 0.35),
                blurRadius: _glow.value,
                spreadRadius: 0,
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const StatusIndicator(type: IndicatorType.live, size: 6),
              const SizedBox(width: 4),
              const Text(
                'LIVE',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.6,
                  color: EbsColors.danger,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
