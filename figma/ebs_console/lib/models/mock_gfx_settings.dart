class MockGfxSettings {
  // Layout
  final String boardPosition;
  final String playerLayout;
  final double xMargin;
  final double topMargin;
  final double botMargin;
  final double headsUpCustomY;

  // Card & Player
  final String revealPlayers;
  final String showFold;
  final double foldDelayTime;
  final String revealCards;
  final bool showHeadsUpHistory;
  final double actionClockThreshold;

  // Numbers
  final Map<String, String> chipPrecision;
  final Map<String, String> displayMode;
  final String currencySymbol;
  final bool trailingZeros;
  final bool divideBy100;

  // Rules
  final bool moveButtonAfterBombPot;
  final int limitRaises;
  final bool straddleEnabled;
  final bool sleeperEnabled;
  final String equityShowTiming;
  final String playerOrdering;
  final bool winningHandHighlight;
  final bool addSeatNumber;
  final bool showEliminated;
  final bool allowRabbitHunting;
  final bool displaySidePot;

  // Leaderboard
  final bool knockoutRank;
  final bool chipcountPercent;
  final bool showEliminatedLeaderboard;
  final bool cumulativeScore;
  final bool hideOnHand;
  final int maxBBDisplay;

  // Animation
  final String transitionIn;
  final double transitionInTime;
  final String transitionOut;
  final double transitionOutTime;
  final bool indentActionPlayer;
  final bool bounceActionPlayer;

  // Branding
  final String? sponsorLogo1;
  final String? sponsorLogo2;
  final String vanityText;
  final bool replaceWithGameVariant;
  final String blindsDisplay;
  final bool showHandWithBlinds;

  // Outs/Equity
  final String showOutsPosition;
  final bool trueOuts;
  final String scoreStripMode;

  const MockGfxSettings({
    this.boardPosition = 'Centre',
    this.playerLayout = 'Horizontal',
    this.xMargin = 0.04,
    this.topMargin = 0.05,
    this.botMargin = 0.04,
    this.headsUpCustomY = 0.5,
    this.revealPlayers = 'Immediate',
    this.showFold = 'Immediate',
    this.foldDelayTime = 3.0,
    this.revealCards = 'Immediate',
    this.showHeadsUpHistory = true,
    this.actionClockThreshold = 15.0,
    this.chipPrecision = const {
      'Player Stack': 'Smart',
      'Player Action': 'Smart',
      'Pot': 'Smart',
      'Blinds': 'Exact',
      'Leaderboard': 'Smart',
      'Chipcounts': 'Smart+Extra',
      'Ticker': 'Smart',
      'Twitch Bot': 'Exact',
    },
    this.displayMode = const {
      'Chipcounts': 'Amount',
      'Pot': 'Amount',
      'Bets': 'Amount',
    },
    this.currencySymbol = '\$',
    this.trailingZeros = false,
    this.divideBy100 = false,
    this.moveButtonAfterBombPot = false,
    this.limitRaises = 4,
    this.straddleEnabled = false,
    this.sleeperEnabled = false,
    this.equityShowTiming = 'After All-In',
    this.playerOrdering = 'Clockwise',
    this.winningHandHighlight = true,
    this.addSeatNumber = true,
    this.showEliminated = true,
    this.allowRabbitHunting = false,
    this.displaySidePot = true,
    this.knockoutRank = true,
    this.chipcountPercent = false,
    this.showEliminatedLeaderboard = true,
    this.cumulativeScore = false,
    this.hideOnHand = false,
    this.maxBBDisplay = 999,
    this.transitionIn = 'Slide',
    this.transitionInTime = 0.5,
    this.transitionOut = 'Fade',
    this.transitionOutTime = 0.3,
    this.indentActionPlayer = true,
    this.bounceActionPlayer = true,
    this.sponsorLogo1,
    this.sponsorLogo2,
    this.vanityText = 'BRACELET STUDIO',
    this.replaceWithGameVariant = false,
    this.blindsDisplay = 'Every Hand',
    this.showHandWithBlinds = true,
    this.showOutsPosition = 'Below',
    this.trueOuts = true,
    this.scoreStripMode = 'Compact',
  });

  MockGfxSettings copyWith({
    String? boardPosition,
    String? playerLayout,
    double? xMargin,
    double? topMargin,
    double? botMargin,
    double? headsUpCustomY,
    String? revealPlayers,
    String? showFold,
    double? foldDelayTime,
    String? revealCards,
    bool? showHeadsUpHistory,
    double? actionClockThreshold,
    Map<String, String>? chipPrecision,
    Map<String, String>? displayMode,
    String? currencySymbol,
    bool? trailingZeros,
    bool? divideBy100,
    bool? moveButtonAfterBombPot,
    int? limitRaises,
    bool? straddleEnabled,
    bool? sleeperEnabled,
    String? equityShowTiming,
    String? playerOrdering,
    bool? winningHandHighlight,
    bool? addSeatNumber,
    bool? showEliminated,
    bool? allowRabbitHunting,
    bool? displaySidePot,
    bool? knockoutRank,
    bool? chipcountPercent,
    bool? showEliminatedLeaderboard,
    bool? cumulativeScore,
    bool? hideOnHand,
    int? maxBBDisplay,
    String? transitionIn,
    double? transitionInTime,
    String? transitionOut,
    double? transitionOutTime,
    bool? indentActionPlayer,
    bool? bounceActionPlayer,
    String? sponsorLogo1,
    String? sponsorLogo2,
    String? vanityText,
    bool? replaceWithGameVariant,
    String? blindsDisplay,
    bool? showHandWithBlinds,
    String? showOutsPosition,
    bool? trueOuts,
    String? scoreStripMode,
  }) {
    return MockGfxSettings(
      boardPosition: boardPosition ?? this.boardPosition,
      playerLayout: playerLayout ?? this.playerLayout,
      xMargin: xMargin ?? this.xMargin,
      topMargin: topMargin ?? this.topMargin,
      botMargin: botMargin ?? this.botMargin,
      headsUpCustomY: headsUpCustomY ?? this.headsUpCustomY,
      revealPlayers: revealPlayers ?? this.revealPlayers,
      showFold: showFold ?? this.showFold,
      foldDelayTime: foldDelayTime ?? this.foldDelayTime,
      revealCards: revealCards ?? this.revealCards,
      showHeadsUpHistory: showHeadsUpHistory ?? this.showHeadsUpHistory,
      actionClockThreshold: actionClockThreshold ?? this.actionClockThreshold,
      chipPrecision: chipPrecision ?? this.chipPrecision,
      displayMode: displayMode ?? this.displayMode,
      currencySymbol: currencySymbol ?? this.currencySymbol,
      trailingZeros: trailingZeros ?? this.trailingZeros,
      divideBy100: divideBy100 ?? this.divideBy100,
      moveButtonAfterBombPot: moveButtonAfterBombPot ?? this.moveButtonAfterBombPot,
      limitRaises: limitRaises ?? this.limitRaises,
      straddleEnabled: straddleEnabled ?? this.straddleEnabled,
      sleeperEnabled: sleeperEnabled ?? this.sleeperEnabled,
      equityShowTiming: equityShowTiming ?? this.equityShowTiming,
      playerOrdering: playerOrdering ?? this.playerOrdering,
      winningHandHighlight: winningHandHighlight ?? this.winningHandHighlight,
      addSeatNumber: addSeatNumber ?? this.addSeatNumber,
      showEliminated: showEliminated ?? this.showEliminated,
      allowRabbitHunting: allowRabbitHunting ?? this.allowRabbitHunting,
      displaySidePot: displaySidePot ?? this.displaySidePot,
      knockoutRank: knockoutRank ?? this.knockoutRank,
      chipcountPercent: chipcountPercent ?? this.chipcountPercent,
      showEliminatedLeaderboard: showEliminatedLeaderboard ?? this.showEliminatedLeaderboard,
      cumulativeScore: cumulativeScore ?? this.cumulativeScore,
      hideOnHand: hideOnHand ?? this.hideOnHand,
      maxBBDisplay: maxBBDisplay ?? this.maxBBDisplay,
      transitionIn: transitionIn ?? this.transitionIn,
      transitionInTime: transitionInTime ?? this.transitionInTime,
      transitionOut: transitionOut ?? this.transitionOut,
      transitionOutTime: transitionOutTime ?? this.transitionOutTime,
      indentActionPlayer: indentActionPlayer ?? this.indentActionPlayer,
      bounceActionPlayer: bounceActionPlayer ?? this.bounceActionPlayer,
      sponsorLogo1: sponsorLogo1 ?? this.sponsorLogo1,
      sponsorLogo2: sponsorLogo2 ?? this.sponsorLogo2,
      vanityText: vanityText ?? this.vanityText,
      replaceWithGameVariant: replaceWithGameVariant ?? this.replaceWithGameVariant,
      blindsDisplay: blindsDisplay ?? this.blindsDisplay,
      showHandWithBlinds: showHandWithBlinds ?? this.showHandWithBlinds,
      showOutsPosition: showOutsPosition ?? this.showOutsPosition,
      trueOuts: trueOuts ?? this.trueOuts,
      scoreStripMode: scoreStripMode ?? this.scoreStripMode,
    );
  }
}
