import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/mock_outputs_settings.dart';

class OutputsSettingsNotifier extends StateNotifier<MockOutputsSettings> {
  OutputsSettingsNotifier() : super(const MockOutputsSettings());

  void setVideoSize(String v) => state = state.copyWith(videoSize: v);
  void toggleVerticalMode() =>
      state = state.copyWith(verticalMode: !state.verticalMode);
  void setFrameRate(int v) => state = state.copyWith(frameRate: v);
  void setNdiOutput(String v) => state = state.copyWith(ndiOutput: v);
  void setDeckLinkOutput(String v) => state = state.copyWith(deckLinkOutput: v);
  void setAudioPreview(String v) => state = state.copyWith(audioPreview: v);
  void toggleFillAndKey() =>
      state = state.copyWith(fillAndKeyEnabled: !state.fillAndKeyEnabled);
  void setColorSpace(String v) => state = state.copyWith(colorSpace: v);
  void setBitDepth(String v) => state = state.copyWith(bitDepth: v);
}

final outputsSettingsProvider =
    StateNotifierProvider<OutputsSettingsNotifier, MockOutputsSettings>(
        (ref) => OutputsSettingsNotifier());
