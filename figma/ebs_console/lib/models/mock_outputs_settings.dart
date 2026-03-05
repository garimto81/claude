import 'package:flutter/material.dart';

class MockOutputsSettings {
  final String videoSize;
  final bool verticalMode;
  final int frameRate;
  final String ndiOutput;
  final String deckLinkOutput;
  final String audioPreview;
  final bool fillAndKeyEnabled;
  final Color keyColor;
  final String colorSpace;
  final String bitDepth;

  const MockOutputsSettings({
    this.videoSize = '1920x1080',
    this.verticalMode = false,
    this.frameRate = 60,
    this.ndiOutput = 'Disabled',
    this.deckLinkOutput = 'DeckLink 4K Extreme',
    this.audioPreview = 'Default',
    this.fillAndKeyEnabled = true,
    this.keyColor = const Color(0xFF000000),
    this.colorSpace = 'BT.709',
    this.bitDepth = '8-bit',
  });

  MockOutputsSettings copyWith({
    String? videoSize,
    bool? verticalMode,
    int? frameRate,
    String? ndiOutput,
    String? deckLinkOutput,
    String? audioPreview,
    bool? fillAndKeyEnabled,
    Color? keyColor,
    String? colorSpace,
    String? bitDepth,
  }) {
    return MockOutputsSettings(
      videoSize: videoSize ?? this.videoSize,
      verticalMode: verticalMode ?? this.verticalMode,
      frameRate: frameRate ?? this.frameRate,
      ndiOutput: ndiOutput ?? this.ndiOutput,
      deckLinkOutput: deckLinkOutput ?? this.deckLinkOutput,
      audioPreview: audioPreview ?? this.audioPreview,
      fillAndKeyEnabled: fillAndKeyEnabled ?? this.fillAndKeyEnabled,
      keyColor: keyColor ?? this.keyColor,
      colorSpace: colorSpace ?? this.colorSpace,
      bitDepth: bitDepth ?? this.bitDepth,
    );
  }
}
