import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/mock_sources_settings.dart';

class SourcesSettingsNotifier extends StateNotifier<MockSourcesSettings> {
  SourcesSettingsNotifier() : super(const MockSourcesSettings());

  void setCameraMode(String v) => state = state.copyWith(cameraMode: v);
  void toggleChromaKey() =>
      state = state.copyWith(chromaKeyEnabled: !state.chromaKeyEnabled);
  void setChromaKeyIntensity(double v) =>
      state = state.copyWith(chromaKeyIntensity: v);
  void setCrossfadeDuration(double v) =>
      state = state.copyWith(crossfadeDuration: v);
  void setAtemIp(String? v) => state = state.copyWith(atemIp: v);
  void setAudioInput(String v) => state = state.copyWith(audioInput: v);
  void setBoardSyncOffsetX(double v) =>
      state = state.copyWith(boardSyncOffsetX: v);
  void setBoardSyncOffsetY(double v) =>
      state = state.copyWith(boardSyncOffsetY: v);
}

final sourcesSettingsProvider =
    StateNotifierProvider<SourcesSettingsNotifier, MockSourcesSettings>(
        (ref) => SourcesSettingsNotifier());
