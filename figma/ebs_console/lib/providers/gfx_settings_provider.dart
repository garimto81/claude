import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/mock_gfx_settings.dart';

class GfxSettingsNotifier extends StateNotifier<MockGfxSettings> {
  GfxSettingsNotifier() : super(const MockGfxSettings());

  // Layout
  void setBoardPosition(String v) => state = state.copyWith(boardPosition: v);
  void setPlayerLayout(String v) => state = state.copyWith(playerLayout: v);
  void setXMargin(double v) => state = state.copyWith(xMargin: v);
  void setTopMargin(double v) => state = state.copyWith(topMargin: v);
  void setBotMargin(double v) => state = state.copyWith(botMargin: v);
  void setHeadsUpCustomY(double v) => state = state.copyWith(headsUpCustomY: v);

  // Card & Player
  void setRevealPlayers(String v) => state = state.copyWith(revealPlayers: v);
  void setShowFold(String v) => state = state.copyWith(showFold: v);
  void setFoldDelayTime(double v) => state = state.copyWith(foldDelayTime: v);
  void setRevealCards(String v) => state = state.copyWith(revealCards: v);
  void toggleShowHeadsUpHistory() =>
      state = state.copyWith(showHeadsUpHistory: !state.showHeadsUpHistory);
  void setActionClockThreshold(double v) =>
      state = state.copyWith(actionClockThreshold: v);

  // Numbers
  void setChipPrecision(String area, String value) {
    final updated = Map<String, String>.from(state.chipPrecision);
    updated[area] = value;
    state = state.copyWith(chipPrecision: updated);
  }

  void setDisplayMode(String area, String value) {
    final updated = Map<String, String>.from(state.displayMode);
    updated[area] = value;
    state = state.copyWith(displayMode: updated);
  }

  void setCurrencySymbol(String v) => state = state.copyWith(currencySymbol: v);
  void toggleTrailingZeros() =>
      state = state.copyWith(trailingZeros: !state.trailingZeros);
  void toggleDivideBy100() =>
      state = state.copyWith(divideBy100: !state.divideBy100);

  // Rules
  void toggleMoveButton() =>
      state = state.copyWith(moveButtonAfterBombPot: !state.moveButtonAfterBombPot);
  void setLimitRaises(int v) => state = state.copyWith(limitRaises: v);
  void toggleStraddle() =>
      state = state.copyWith(straddleEnabled: !state.straddleEnabled);
  void toggleSleeper() =>
      state = state.copyWith(sleeperEnabled: !state.sleeperEnabled);
  void setEquityShowTiming(String v) =>
      state = state.copyWith(equityShowTiming: v);
  void setPlayerOrdering(String v) =>
      state = state.copyWith(playerOrdering: v);
  void toggleWinningHandHighlight() =>
      state = state.copyWith(winningHandHighlight: !state.winningHandHighlight);
  void toggleAddSeatNumber() =>
      state = state.copyWith(addSeatNumber: !state.addSeatNumber);
  void toggleShowEliminated() =>
      state = state.copyWith(showEliminated: !state.showEliminated);
  void toggleRabbitHunting() =>
      state = state.copyWith(allowRabbitHunting: !state.allowRabbitHunting);
  void toggleDisplaySidePot() =>
      state = state.copyWith(displaySidePot: !state.displaySidePot);

  // Leaderboard
  void toggleKnockoutRank() =>
      state = state.copyWith(knockoutRank: !state.knockoutRank);
  void toggleChipcountPercent() =>
      state = state.copyWith(chipcountPercent: !state.chipcountPercent);
  void toggleShowEliminatedLeaderboard() =>
      state = state.copyWith(showEliminatedLeaderboard: !state.showEliminatedLeaderboard);
  void toggleCumulativeScore() =>
      state = state.copyWith(cumulativeScore: !state.cumulativeScore);
  void toggleHideOnHand() =>
      state = state.copyWith(hideOnHand: !state.hideOnHand);
  void setMaxBBDisplay(int v) => state = state.copyWith(maxBBDisplay: v);

  // Animation
  void setTransitionIn(String v) => state = state.copyWith(transitionIn: v);
  void setTransitionInTime(double v) =>
      state = state.copyWith(transitionInTime: v);
  void setTransitionOut(String v) => state = state.copyWith(transitionOut: v);
  void setTransitionOutTime(double v) =>
      state = state.copyWith(transitionOutTime: v);
  void toggleIndentActionPlayer() =>
      state = state.copyWith(indentActionPlayer: !state.indentActionPlayer);
  void toggleBounceActionPlayer() =>
      state = state.copyWith(bounceActionPlayer: !state.bounceActionPlayer);

  // Branding
  void setVanityText(String v) => state = state.copyWith(vanityText: v);
  void toggleReplaceWithGameVariant() =>
      state = state.copyWith(replaceWithGameVariant: !state.replaceWithGameVariant);
  void setBlindsDisplay(String v) => state = state.copyWith(blindsDisplay: v);
  void toggleShowHandWithBlinds() =>
      state = state.copyWith(showHandWithBlinds: !state.showHandWithBlinds);

  // Outs/Equity
  void setShowOutsPosition(String v) =>
      state = state.copyWith(showOutsPosition: v);
  void toggleTrueOuts() =>
      state = state.copyWith(trueOuts: !state.trueOuts);
  void setScoreStripMode(String v) =>
      state = state.copyWith(scoreStripMode: v);
}

final gfxSettingsProvider =
    StateNotifierProvider<GfxSettingsNotifier, MockGfxSettings>(
        (ref) => GfxSettingsNotifier());
