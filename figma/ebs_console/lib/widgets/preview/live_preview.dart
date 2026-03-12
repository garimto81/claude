import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/ebs_colors.dart';
import '../../providers/game_state_provider.dart';
import '../../models/mock_player.dart';

String _formatNumber(int n) {
  final s = n.toString();
  final result = StringBuffer();
  for (var i = 0; i < s.length; i++) {
    if (i > 0 && (s.length - i) % 3 == 0) result.write(',');
    result.write(s[i]);
  }
  return result.toString();
}

class LivePreview extends ConsumerWidget {
  const LivePreview({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final game = ref.watch(gameStateProvider);

    return Container(
      color: EbsColors.bgPrimary,
      child: Center(
        child: AspectRatio(
          aspectRatio: 16 / 9,
          child: Container(
            decoration: BoxDecoration(
              color: const Color(0xFF0000FF),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Stack(
              children: [
                // Center: POT display
                Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'POT',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1.1,
                          color: Colors.white.withValues(alpha: 0.6),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '\$${_formatNumber(game.potAmount)}',
                        style: GoogleFonts.jetBrainsMono(
                          fontSize: 28,
                          fontWeight: FontWeight.w700,
                          color: EbsColors.accentGold,
                          fontFeatures: const [FontFeature.tabularFigures()],
                          shadows: const [
                            Shadow(
                              color: Color(0x55D4AF37),
                              blurRadius: 12,
                            ),
                          ],
                        ),
                      ),
                      if (game.sidePots.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            for (int i = 0; i < game.sidePots.length; i++) ...[
                              if (i > 0) const SizedBox(width: 8),
                              Text(
                                'SP${i + 1}: \$${_formatNumber(game.sidePots[i])}',
                                style: GoogleFonts.jetBrainsMono(
                                  fontSize: 11,
                                  color: Colors.white.withValues(alpha: 0.5),
                                ),
                              ),
                            ],
                          ],
                        ),
                      ],
                      const SizedBox(height: 8),
                      // Board cards
                      if (game.boardCards.any((c) => c.isNotEmpty))
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            for (final card in game.boardCards)
                              if (card.isNotEmpty)
                                _CardChip(card: card, size: 14),
                          ],
                        ),
                      const SizedBox(height: 12),
                      Text(
                        'LIVE PREVIEW',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 2.7,
                          color: Colors.white.withValues(alpha: 0.3),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Chroma-key ready \u2014 16:9',
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.white.withValues(alpha: 0.25),
                        ),
                      ),
                    ],
                  ),
                ),
                // Player slots at bottom
                Positioned(
                  left: 0,
                  right: 0,
                  bottom: 0,
                  child: _PlayerStrip(players: game.players),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

}

/// Suit-aware card chip used in board and player hole cards.
class _CardChip extends StatelessWidget {
  final String card;
  final double size;
  const _CardChip({required this.card, this.size = 12});

  bool get _isRed {
    if (card.isEmpty) return false;
    final suit = card[card.length - 1];
    return suit == 'h' || suit == 'd';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 2),
      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 3),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(3),
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
          fontSize: size,
          fontWeight: FontWeight.w800,
          color: _isRed ? const Color(0xFFCC1111) : Colors.black,
        ),
      ),
    );
  }
}

class _PlayerStrip extends StatelessWidget {
  final List<MockPlayer> players;
  const _PlayerStrip({required this.players});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(6),
      child: Row(
        children: [
          for (int i = 0; i < players.length; i++) ...[
            if (i > 0) const SizedBox(width: 3),
            Expanded(child: _PlayerSlotMini(player: players[i])),
          ],
        ],
      ),
    );
  }
}

class _PlayerSlotMini extends StatelessWidget {
  final MockPlayer player;
  const _PlayerSlotMini({required this.player});

  Color _actionColor(String action) => switch (action.toUpperCase()) {
        'BET' || 'RAISE' => EbsColors.accentGold,
        'CALL' || 'CHECK' => EbsColors.accentBlue,
        'FOLD' => EbsColors.textMuted,
        'ALL-IN' || 'ALLIN' => EbsColors.accentNeon,
        _ => EbsColors.textMuted,
      };

  @override
  Widget build(BuildContext context) {
    final occupied = !player.isEmpty;
    final folded = player.isFolded;
    final allIn = player.isAllIn;
    final hasAction = player.action != null && player.action!.isNotEmpty;

    final borderColor = allIn
        ? EbsColors.accentNeon.withValues(alpha: 0.7)
        : occupied
            ? EbsColors.accentGold.withValues(alpha: 0.35)
            : Colors.white.withValues(alpha: 0.1);

    return AnimatedOpacity(
      duration: const Duration(milliseconds: 200),
      opacity: occupied ? (folded ? 0.38 : 1.0) : 0.25,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 5),
        decoration: BoxDecoration(
          color: Colors.black.withValues(alpha: 0.6),
          border: Border.all(color: borderColor),
          borderRadius: BorderRadius.circular(3),
          boxShadow: allIn
              ? [
                  BoxShadow(
                    color: EbsColors.accentNeon.withValues(alpha: 0.25),
                    blurRadius: 8,
                  ),
                ]
              : null,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
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
                      color: Colors.white.withValues(alpha: 0.85),
                    ),
                    textAlign: TextAlign.center,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            if (occupied) ...[
              const SizedBox(height: 2),
              Text(
                '\$${_formatNumber(player.stack)}',
                style: GoogleFonts.jetBrainsMono(
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                  color: EbsColors.accentGold,
                ),
                textAlign: TextAlign.center,
              ),
              // Hole cards
              if (player.holeCards.isNotEmpty) ...[
                const SizedBox(height: 3),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    for (final card in player.holeCards)
                      _CardChip(card: card, size: 9),
                  ],
                ),
              ],
              // Action badge
              if (hasAction) ...[
                const SizedBox(height: 3),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                  decoration: BoxDecoration(
                    color: _actionColor(player.action!).withValues(alpha: 0.18),
                    border: Border.all(
                      color: _actionColor(player.action!).withValues(alpha: 0.4),
                    ),
                    borderRadius: BorderRadius.circular(2),
                  ),
                  child: Text(
                    player.action!.toUpperCase(),
                    style: TextStyle(
                      fontSize: 8,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 0.5,
                      color: _actionColor(player.action!),
                    ),
                  ),
                ),
              ],
              if (player.equity != null) ...[
                const SizedBox(height: 3),
                _EquityBar(equity: player.equity!),
              ],
            ],
          ],
        ),
      ),
    );
  }
}

class _EquityBar extends StatelessWidget {
  final double equity;
  const _EquityBar({required this.equity});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 3,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(1.5),
        child: LinearProgressIndicator(
          value: equity,
          backgroundColor: Colors.white.withValues(alpha: 0.1),
          valueColor: const AlwaysStoppedAnimation<Color>(EbsColors.equityBar),
        ),
      ),
    );
  }
}
