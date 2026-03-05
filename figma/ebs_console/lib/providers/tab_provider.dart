import 'package:flutter_riverpod/flutter_riverpod.dart';

// Active tab index (0=Sources, 1=Outputs, 2=GFX, 3=System)
final activeTabProvider = StateProvider<int>((ref) => 0);

// Command palette visibility
final commandPaletteVisibleProvider = StateProvider<bool>((ref) => false);

// GFX section expanded states (Layout default expanded, rest collapsed)
final gfxLayoutExpandedProvider = StateProvider<bool>((ref) => true);
final gfxCardPlayerExpandedProvider = StateProvider<bool>((ref) => false);
final gfxAnimationExpandedProvider = StateProvider<bool>((ref) => false);
final gfxNumbersExpandedProvider = StateProvider<bool>((ref) => false);
final gfxRulesExpandedProvider = StateProvider<bool>((ref) => false);
final gfxBrandingExpandedProvider = StateProvider<bool>((ref) => false);

// Shortcut guide visibility
final shortcutGuideVisibleProvider = StateProvider<bool>((ref) => false);
