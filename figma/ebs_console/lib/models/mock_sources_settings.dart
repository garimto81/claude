import 'package:flutter/material.dart';

class MockSourcesSettings {
  final String cameraMode;
  final bool chromaKeyEnabled;
  final Color chromaKeyColor;
  final double chromaKeyIntensity;
  final double crossfadeDuration;
  final String? atemIp;
  final String audioInput;
  final double boardSyncOffsetX;
  final double boardSyncOffsetY;

  const MockSourcesSettings({
    this.cameraMode = 'STATIC',
    this.chromaKeyEnabled = true,
    this.chromaKeyColor = const Color(0xFF0000FF),
    this.chromaKeyIntensity = 0.85,
    this.crossfadeDuration = 0.5,
    this.atemIp,
    this.audioInput = 'Default',
    this.boardSyncOffsetX = 0.0,
    this.boardSyncOffsetY = 0.0,
  });

  MockSourcesSettings copyWith({
    String? cameraMode,
    bool? chromaKeyEnabled,
    Color? chromaKeyColor,
    double? chromaKeyIntensity,
    double? crossfadeDuration,
    String? atemIp,
    String? audioInput,
    double? boardSyncOffsetX,
    double? boardSyncOffsetY,
  }) {
    return MockSourcesSettings(
      cameraMode: cameraMode ?? this.cameraMode,
      chromaKeyEnabled: chromaKeyEnabled ?? this.chromaKeyEnabled,
      chromaKeyColor: chromaKeyColor ?? this.chromaKeyColor,
      chromaKeyIntensity: chromaKeyIntensity ?? this.chromaKeyIntensity,
      crossfadeDuration: crossfadeDuration ?? this.crossfadeDuration,
      atemIp: atemIp ?? this.atemIp,
      audioInput: audioInput ?? this.audioInput,
      boardSyncOffsetX: boardSyncOffsetX ?? this.boardSyncOffsetX,
      boardSyncOffsetY: boardSyncOffsetY ?? this.boardSyncOffsetY,
    );
  }
}
