class MockPlayer {
  final int seat;
  final String name;
  final int stack;
  final List<String> holeCards;
  final String position;
  final double? equity;
  final bool isActive;
  final bool isDealer;
  final bool isFolded;
  final bool isAllIn;
  final bool isEliminated;
  final String? action;
  final int? actionAmount;
  final String? country;

  const MockPlayer({
    required this.seat,
    required this.name,
    required this.stack,
    this.holeCards = const [],
    this.position = '',
    this.equity,
    this.isActive = true,
    this.isDealer = false,
    this.isFolded = false,
    this.isAllIn = false,
    this.isEliminated = false,
    this.action,
    this.actionAmount,
    this.country,
  });

  bool get isEmpty => name.isEmpty;

  MockPlayer copyWith({
    int? seat,
    String? name,
    int? stack,
    List<String>? holeCards,
    String? position,
    double? equity,
    bool? isActive,
    bool? isDealer,
    bool? isFolded,
    bool? isAllIn,
    bool? isEliminated,
    String? action,
    int? actionAmount,
    String? country,
  }) {
    return MockPlayer(
      seat: seat ?? this.seat,
      name: name ?? this.name,
      stack: stack ?? this.stack,
      holeCards: holeCards ?? this.holeCards,
      position: position ?? this.position,
      equity: equity ?? this.equity,
      isActive: isActive ?? this.isActive,
      isDealer: isDealer ?? this.isDealer,
      isFolded: isFolded ?? this.isFolded,
      isAllIn: isAllIn ?? this.isAllIn,
      isEliminated: isEliminated ?? this.isEliminated,
      action: action ?? this.action,
      actionAmount: actionAmount ?? this.actionAmount,
      country: country ?? this.country,
    );
  }
}
