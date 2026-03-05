import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/ebs_colors.dart';
import '../../models/mock_player.dart';

class PlayerSlot extends StatelessWidget {
  final MockPlayer player;

  const PlayerSlot({super.key, required this.player});

  @override
  Widget build(BuildContext context) {
    final occupied = !player.isEmpty;
    final folded = player.isFolded;
    final allIn = player.isAllIn;
    final eliminated = player.isEliminated;

    return AnimatedOpacity(
      duration: const Duration(milliseconds: 200),
      opacity: occupied
          ? (eliminated ? 0.2 : folded ? 0.4 : 1.0)
          : 0.3,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 5),
        decoration: BoxDecoration(
          color: Colors.black.withValues(alpha: 0.55),
          border: Border.all(
            color: allIn
                ? EbsColors.accentNeon.withValues(alpha: 0.7)
                : occupied
                    ? EbsColors.accentGold.withValues(alpha: 0.4)
                    : Colors.white.withValues(alpha: 0.15),
            width: allIn ? 1.5 : 1.0,
          ),
          borderRadius: BorderRadius.circular(3),
          boxShadow: allIn
              ? [
                  BoxShadow(
                    color: EbsColors.accentNeon.withValues(alpha: 0.3),
                    blurRadius: 8,
                  ),
                ]
              : null,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Position + Name row
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              mainAxisSize: MainAxisSize.min,
              children: [
                if (player.position.isNotEmpty) ...[
                  Text(
                    player.position,
                    style: TextStyle(
                      fontSize: 8,
                      fontWeight: FontWeight.w700,
                      color: player.isDealer
                          ? EbsColors.accentGold
                          : EbsColors.textMuted,
                    ),
                  ),
                  const SizedBox(width: 3),
                ],
                Flexible(
                  child: Text(
                    occupied ? player.name : 'P${player.seat}',
                    style: TextStyle(
                      fontSize: 9,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.54,
                      color: Colors.white.withValues(alpha: 0.8),
                    ),
                    textAlign: TextAlign.center,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            if (occupied) ...[
              const SizedBox(height: 2),
              // Stack in accentGold mono
              Text(
                _formatStack(player.stack),
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: EbsColors.accentGold,
                  fontFeatures: const [FontFeature.tabularFigures()],
                ),
                textAlign: TextAlign.center,
              ),
              // Hole cards as card-shaped containers
              if (player.holeCards.isNotEmpty) ...[
                const SizedBox(height: 3),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    for (final card in player.holeCards)
                      _CardChip(card: card),
                  ],
                ),
              ],
              // Equity bar
              if (player.equity != null) ...[
                const SizedBox(height: 2),
                SizedBox(
                  height: 3,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(1.5),
                    child: LinearProgressIndicator(
                      value: player.equity!,
                      backgroundColor: Colors.white.withValues(alpha: 0.1),
                      valueColor: const AlwaysStoppedAnimation<Color>(
                        EbsColors.equityBar,
                      ),
                    ),
                  ),
                ),
              ],
              // Action badge
              if (player.action != null) ...[
                const SizedBox(height: 3),
                _ActionBadge(
                  action: player.action!,
                  amount: player.actionAmount,
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }

  String _formatStack(int n) {
    final s = n.toString();
    final result = StringBuffer();
    for (var i = 0; i < s.length; i++) {
      if (i > 0 && (s.length - i) % 3 == 0) result.write(',');
      result.write(s[i]);
    }
    return result.toString();
  }
}

class _CardChip extends StatelessWidget {
  final String card;
  const _CardChip({required this.card});

  Color _suitColor(String card) {
    if (card.isEmpty) return Colors.black;
    final suit = card[card.length - 1];
    return switch (suit) {
      'h' || 'd' => const Color(0xFFE53935),
      _ => Colors.black,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 1),
      padding: const EdgeInsets.symmetric(horizontal: 3, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(2),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.4),
            blurRadius: 3,
            offset: const Offset(0, 1),
          ),
        ],
      ),
      child: Text(
        card,
        style: GoogleFonts.jetBrainsMono(
          fontSize: 8,
          fontWeight: FontWeight.w700,
          color: _suitColor(card),
        ),
      ),
    );
  }
}

class _ActionBadge extends StatelessWidget {
  final String action;
  final int? amount;
  const _ActionBadge({required this.action, this.amount});

  (Color bg, Color fg) _colors(String action) {
    return switch (action.toUpperCase()) {
      'BET' || 'RAISE' => (
          EbsColors.accentGold.withValues(alpha: 0.2),
          EbsColors.accentGold,
        ),
      'CALL' => (
          EbsColors.accentBlue.withValues(alpha: 0.2),
          EbsColors.accentBlue,
        ),
      'FOLD' => (
          EbsColors.textMuted.withValues(alpha: 0.2),
          EbsColors.textMuted,
        ),
      'ALL-IN' || 'ALLIN' => (
          EbsColors.accentNeon.withValues(alpha: 0.2),
          EbsColors.accentNeon,
        ),
      _ => (
          EbsColors.accentBlue.withValues(alpha: 0.15),
          EbsColors.accentBlue,
        ),
    };
  }

  String _formatStack(int n) {
    final s = n.toString();
    final result = StringBuffer();
    for (var i = 0; i < s.length; i++) {
      if (i > 0 && (s.length - i) % 3 == 0) result.write(',');
      result.write(s[i]);
    }
    return result.toString();
  }

  @override
  Widget build(BuildContext context) {
    final (bg, fg) = _colors(action);
    final label =
        amount != null ? '$action ${_formatStack(amount!)}' : action;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(2),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 7,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.3,
          color: fg,
        ),
      ),
    );
  }
}
