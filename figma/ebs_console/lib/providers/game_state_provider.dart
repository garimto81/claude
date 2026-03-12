import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/mock_game_state.dart';
import '../models/mock_player.dart';

class GameStateNotifier extends StateNotifier<MockGameState> {
  GameStateNotifier() : super(_initialState);

  void updateTableName(String name) => state = state.copyWith(tableName: name);
  void updateGamePhase(String phase) => state = state.copyWith(gamePhase: phase);
  void updatePot(int pot) => state = state.copyWith(potAmount: pot);
  void toggleLive() => state = state.copyWith(isLive: !state.isLive);

  static const _initialState = MockGameState(
    tableName: 'Main Event #3',
    gameType: 'NLHE',
    gamePhase: 'FLOP',
    handNumber: 247,
    potAmount: 2450,
    sidePots: [1200, 800],
    smallBlind: 50,
    bigBlind: 100,
    ante: 0,
    boardCards: ['As', 'Kh', '7d', '', ''],
    activePlayers: 4,
    isLive: true,
    delay: Duration(seconds: 28),
    players: [
      MockPlayer(
        seat: 1, name: 'KIM', stack: 48200,
        holeCards: ['Ah', 'Ks'], position: 'BTN',
        equity: 0.65, isDealer: true, country: 'KR',
      ),
      MockPlayer(seat: 2, name: '', stack: 0, isActive: false),
      MockPlayer(
        seat: 3, name: 'LEE', stack: 31750,
        holeCards: ['Qd', 'Jd'], position: 'SB',
        equity: 0.22, country: 'KR',
      ),
      MockPlayer(seat: 4, name: '', stack: 0, isActive: false),
      MockPlayer(
        seat: 5, name: 'PARK', stack: 12900,
        holeCards: ['9s', '9h'], position: 'BB',
        equity: 0.08, action: 'CHECK', country: 'KR',
      ),
      MockPlayer(seat: 6, name: '', stack: 0, isActive: false),
      MockPlayer(
        seat: 7, name: 'CHOI', stack: 67500,
        holeCards: ['Tc', 'Td'], position: 'UTG',
        equity: 0.05, action: 'BET', actionAmount: 200,
        isFolded: true, country: 'KR',
      ),
      MockPlayer(seat: 8, name: '', stack: 0, isActive: false),
      MockPlayer(seat: 9, name: '', stack: 0, isActive: false),
    ],
  );
}

final gameStateProvider =
    StateNotifierProvider<GameStateNotifier, MockGameState>(
        (ref) => GameStateNotifier());

// Mock table list for dropdown
final tableListProvider = Provider<List<String>>((ref) => [
  'Main Event #3',
  'Cash Game #1',
  'Cash Game #2',
]);
