import 'mock_player.dart';

class MockGameState {
  final String tableName;
  final String gameType;
  final String gamePhase;
  final int handNumber;
  final int potAmount;
  final List<int> sidePots;
  final int smallBlind;
  final int bigBlind;
  final int ante;
  final List<String> boardCards;
  final List<MockPlayer> players;
  final int activePlayers;
  final String? winningHandName;
  final bool isLive;
  final Duration delay;

  const MockGameState({
    required this.tableName,
    required this.gameType,
    required this.gamePhase,
    required this.handNumber,
    required this.potAmount,
    this.sidePots = const [],
    required this.smallBlind,
    required this.bigBlind,
    this.ante = 0,
    this.boardCards = const [],
    required this.players,
    required this.activePlayers,
    this.winningHandName,
    this.isLive = true,
    this.delay = const Duration(seconds: 28),
  });

  MockGameState copyWith({
    String? tableName,
    String? gameType,
    String? gamePhase,
    int? handNumber,
    int? potAmount,
    List<int>? sidePots,
    int? smallBlind,
    int? bigBlind,
    int? ante,
    List<String>? boardCards,
    List<MockPlayer>? players,
    int? activePlayers,
    String? winningHandName,
    bool? isLive,
    Duration? delay,
  }) {
    return MockGameState(
      tableName: tableName ?? this.tableName,
      gameType: gameType ?? this.gameType,
      gamePhase: gamePhase ?? this.gamePhase,
      handNumber: handNumber ?? this.handNumber,
      potAmount: potAmount ?? this.potAmount,
      sidePots: sidePots ?? this.sidePots,
      smallBlind: smallBlind ?? this.smallBlind,
      bigBlind: bigBlind ?? this.bigBlind,
      ante: ante ?? this.ante,
      boardCards: boardCards ?? this.boardCards,
      players: players ?? this.players,
      activePlayers: activePlayers ?? this.activePlayers,
      winningHandName: winningHandName ?? this.winningHandName,
      isLive: isLive ?? this.isLive,
      delay: delay ?? this.delay,
    );
  }
}
