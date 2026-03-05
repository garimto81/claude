import 'dart:math';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/ebs_colors.dart';
import '../providers/tab_provider.dart';

class CommandItem {
  final String command;
  final String description;
  final String category;

  const CommandItem({
    required this.command,
    required this.description,
    required this.category,
  });
}

const _allCommands = [
  // OVERLAY
  CommandItem(command: 'show gfx', description: 'Show GFX overlay', category: 'OVERLAY'),
  CommandItem(command: 'hide gfx', description: 'Hide GFX overlay', category: 'OVERLAY'),
  CommandItem(command: 'toggle overlay', description: 'Toggle overlay visibility', category: 'OVERLAY'),
  CommandItem(command: 'show leaderboard', description: 'Show Leaderboard overlay', category: 'OVERLAY'),
  CommandItem(command: 'show equity', description: 'Show equity display', category: 'OVERLAY'),
  // SYSTEM
  CommandItem(command: 'reset hand', description: 'Reset current hand', category: 'SYSTEM'),
  CommandItem(command: 'theme dark', description: 'Switch to dark theme', category: 'SYSTEM'),
  CommandItem(command: 'theme light', description: 'Switch to light theme', category: 'SYSTEM'),
  CommandItem(command: 'output 1080p', description: 'Set output to 1080p', category: 'SYSTEM'),
  CommandItem(command: 'output 720p', description: 'Set output to 720p', category: 'SYSTEM'),
  CommandItem(command: 'delay 30', description: 'Set Secure Delay to 30s', category: 'SYSTEM'),
  CommandItem(command: 'export config', description: 'Export configuration', category: 'SYSTEM'),
  // RFID
  CommandItem(command: 'calibrate', description: 'Calibrate RFID antennas', category: 'RFID'),
  CommandItem(command: 'antenna 1', description: 'Select Upcard antenna', category: 'RFID'),
  CommandItem(command: 'antenna 2', description: 'Select Muck antenna', category: 'RFID'),
  CommandItem(command: 'antenna 3', description: 'Select Community antenna', category: 'RFID'),
  CommandItem(command: 'reset rfid', description: 'Reset RFID module', category: 'RFID'),
  CommandItem(command: 'register deck', description: 'Start RFID deck registration', category: 'RFID'),
];

class CommandPalette extends ConsumerStatefulWidget {
  const CommandPalette({super.key});

  @override
  ConsumerState<CommandPalette> createState() => _CommandPaletteState();
}

class _CommandPaletteState extends ConsumerState<CommandPalette> {
  final _controller = TextEditingController();
  late final _focusNode = FocusNode();
  int _selectedIndex = 0;
  List<CommandItem> _filtered = _allCommands;

  @override
  void initState() {
    super.initState();
    _controller.addListener(_onSearchChanged);
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _onSearchChanged() {
    final query = _controller.text.trim().toLowerCase();
    setState(() {
      if (query.isEmpty) {
        _filtered = _allCommands;
      } else {
        _filtered = _allCommands
            .where((item) =>
                item.command.contains(query) ||
                _levenshteinDistance(query, item.command.split(' ').first) <= 2)
            .toList();
      }
      _selectedIndex = 0;
    });
  }

  void _close() {
    ref.read(commandPaletteVisibleProvider.notifier).state = false;
  }

  int _levenshteinDistance(String s, String t) {
    if (s == t) return 0;
    if (s.isEmpty) return t.length;
    if (t.isEmpty) return s.length;

    List<int> v0 = List<int>.generate(t.length + 1, (i) => i);
    List<int> v1 = List<int>.filled(t.length + 1, 0);

    for (int i = 0; i < s.length; i++) {
      v1[0] = i + 1;
      for (int j = 0; j < t.length; j++) {
        final cost = s[i] == t[j] ? 0 : 1;
        v1[j + 1] = [v1[j] + 1, v0[j + 1] + 1, v0[j] + cost].reduce(min);
      }
      final temp = v0;
      v0 = v1;
      v1 = temp;
    }
    return v0[t.length];
  }

  @override
  Widget build(BuildContext context) {
    final grouped = <String, List<CommandItem>>{};
    for (final item in _filtered) {
      grouped.putIfAbsent(item.category, () => []).add(item);
    }

    // O(1) 조회를 위해 아이템 → 글로벌 인덱스 매핑을 한 번만 계산
    final indexMap = <CommandItem, int>{};
    for (var i = 0; i < _filtered.length; i++) {
      indexMap[_filtered[i]] = i;
    }

    return GestureDetector(
      onTap: _close,
      child: Container(
        color: const Color(0xB805050F),
        child: Center(
          child: GestureDetector(
            onTap: () {},
            child: KeyboardListener(
              focusNode: _focusNode,
              onKeyEvent: (event) {
                if (event is KeyDownEvent) {
                  if (event.logicalKey == LogicalKeyboardKey.arrowDown) {
                    setState(() => _selectedIndex = (_selectedIndex + 1).clamp(0, _filtered.length - 1));
                  } else if (event.logicalKey == LogicalKeyboardKey.arrowUp) {
                    setState(() => _selectedIndex = (_selectedIndex - 1).clamp(0, _filtered.length - 1));
                  } else if (event.logicalKey == LogicalKeyboardKey.escape) {
                    _close();
                  }
                }
              },
              child: ClipRRect(
                borderRadius: BorderRadius.circular(EbsColors.borderRadiusLg),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
                  child: Container(
                width: 560,
                decoration: BoxDecoration(
                  color: const Color(0xE8141424),
                  border: Border.all(color: Colors.white.withValues(alpha: 0.14)),
                  borderRadius: BorderRadius.circular(EbsColors.borderRadiusLg),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.7),
                      blurRadius: 64,
                      offset: const Offset(0, 24),
                    ),
                    BoxShadow(
                      color: EbsColors.accentGold.withValues(alpha: 0.06),
                      blurRadius: 48,
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _SearchBar(controller: _controller, onClose: _close),
                    ConstrainedBox(
                      constraints: const BoxConstraints(maxHeight: 360),
                      child: SingleChildScrollView(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            for (final entry in grouped.entries) ...[
                              _SectionLabel(entry.key),
                              for (int i = 0; i < entry.value.length; i++)
                                _ResultRow(
                                  item: entry.value[i],
                                  isSelected: indexMap[entry.value[i]] == _selectedIndex,
                                ),
                            ],
                          ],
                        ),
                      ),
                    ),
                    const _PaletteFooter(),
                  ],
                ),
              ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _SearchBar extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onClose;

  const _SearchBar({required this.controller, required this.onClose});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: Colors.white.withValues(alpha: 0.08))),
      ),
      child: Row(
        children: [
          Container(
            width: 30,
            height: 30,
            decoration: BoxDecoration(
              color: EbsColors.accentGold.withValues(alpha: 0.15),
              border: Border.all(color: EbsColors.accentGold.withValues(alpha: 0.4)),
              borderRadius: BorderRadius.circular(6),
            ),
            alignment: Alignment.center,
            child: const Text(
              '\u2318',
              style: TextStyle(fontSize: 14, color: EbsColors.accentGold),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: TextField(
              controller: controller,
              autofocus: true,
              style: GoogleFonts.jetBrainsMono(
                fontSize: 16,
                color: EbsColors.textPrimary,
              ),
              cursorColor: EbsColors.accentGold,
              decoration: InputDecoration(
                hintText: 'Type a command...',
                hintStyle: GoogleFonts.jetBrainsMono(
                  fontSize: 16,
                  color: EbsColors.textMuted,
                ),
                border: InputBorder.none,
                isDense: true,
                contentPadding: EdgeInsets.zero,
              ),
            ),
          ),
          GestureDetector(
            onTap: onClose,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.06),
                border: Border.all(color: Colors.white.withValues(alpha: 0.14)),
                borderRadius: BorderRadius.circular(4),
              ),
              child: const Text(
                'ESC',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: EbsColors.textMuted,
                  letterSpacing: 0.44,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String text;
  const _SectionLabel(this.text);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 4),
      child: Text(
        text.toUpperCase(),
        style: const TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.0,
          color: EbsColors.textMuted,
        ),
      ),
    );
  }
}

class _ResultRow extends StatelessWidget {
  final CommandItem item;
  final bool isSelected;

  const _ResultRow({required this.item, required this.isSelected});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      color: isSelected ? EbsColors.accentGold.withValues(alpha: 0.07) : Colors.transparent,
      child: Row(
        children: [
          SizedBox(
            width: 12,
            child: Text(
              '\u00B7',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 11,
                color: isSelected ? EbsColors.accentGold : EbsColors.textMuted,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              item.command,
              style: GoogleFonts.jetBrainsMono(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: EbsColors.textPrimary,
              ),
            ),
          ),
          Expanded(
            child: Text(
              item.description,
              style: const TextStyle(fontSize: 12, color: EbsColors.textMuted),
            ),
          ),
          const SizedBox(width: 8),
          _CategoryBadge(category: item.category),
          const SizedBox(width: 8),
          AnimatedOpacity(
            duration: const Duration(milliseconds: 100),
            opacity: isSelected ? 0.7 : 0.0,
            child: const Text(
              '\u21B5',
              style: TextStyle(fontSize: 10, color: EbsColors.textMuted),
            ),
          ),
        ],
      ),
    );
  }
}

class _CategoryBadge extends StatelessWidget {
  final String category;
  const _CategoryBadge({required this.category});

  @override
  Widget build(BuildContext context) {
    final (bg, border, fg) = switch (category) {
      'OVERLAY' => (
        EbsColors.accentBlue.withValues(alpha: 0.12),
        EbsColors.accentBlue.withValues(alpha: 0.3),
        EbsColors.accentBlue,
      ),
      'RFID' => (
        EbsColors.accentGold.withValues(alpha: 0.15),
        EbsColors.accentGold.withValues(alpha: 0.35),
        EbsColors.accentGold,
      ),
      _ => (
        EbsColors.textMuted.withValues(alpha: 0.25),
        EbsColors.textMuted.withValues(alpha: 0.4),
        EbsColors.textMuted,
      ),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(
        color: bg,
        border: Border.all(color: border),
        borderRadius: BorderRadius.circular(3),
      ),
      child: Text(
        category,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.6,
          color: fg,
        ),
      ),
    );
  }
}

class _PaletteFooter extends StatelessWidget {
  const _PaletteFooter();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.25),
        border: Border(top: BorderSide(color: Colors.white.withValues(alpha: 0.06))),
      ),
      child: Row(
        children: [
          _Shortcut(keys: ['\u2191', '\u2193'], label: 'NAVIGATE'),
          const SizedBox(width: 20),
          _Shortcut(keys: ['\u21B5'], label: 'EXECUTE'),
          const SizedBox(width: 20),
          _Shortcut(keys: ['Esc'], label: 'CLOSE'),
          const SizedBox(width: 20),
          _Shortcut(keys: ['Tab'], label: 'AUTOCOMPLETE'),
        ],
      ),
    );
  }
}

class _Shortcut extends StatelessWidget {
  final List<String> keys;
  final String label;
  const _Shortcut({required this.keys, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (final key in keys)
          Container(
            margin: const EdgeInsets.only(right: 4),
            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.08),
              border: Border.all(color: Colors.white.withValues(alpha: 0.15)),
              borderRadius: BorderRadius.circular(3),
            ),
            child: Text(
              key,
              style: GoogleFonts.jetBrainsMono(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: EbsColors.textSecondary,
              ),
            ),
          ),
        const SizedBox(width: 2),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            letterSpacing: 0.55,
            color: EbsColors.textMuted,
          ),
        ),
      ],
    );
  }
}
