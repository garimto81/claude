import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/mock_system_state.dart';

class SystemStateNotifier extends StateNotifier<MockSystemState> {
  SystemStateNotifier() : super(_initialState);

  void toggleRfid() =>
      state = state.copyWith(rfidConnected: !state.rfidConnected);
  void toggleAtConnected() =>
      state = state.copyWith(atConnected: !state.atConnected);
  void updateCpuUsage(double v) => state = state.copyWith(cpuUsage: v);
  void updateGpuUsage(double v) => state = state.copyWith(gpuUsage: v);

  static const _initialState = MockSystemState(
    rfidConnected: true,
    atConnected: true,
    engineOk: true,
    cpuUsage: 0.12,
    gpuUsage: 0.35,
    memUsage: 0.45,
    cameraMode: 'STATIC',
    chromaKeyEnabled: true,
    chromaKeyColor: Color(0xFF0000FF),
    antennas: [
      MockRfidAntenna(
        name: 'Upcard',
        isConnected: true,
        power: -45,
        sensitivity: 0.85,
        heartbeat: Duration(milliseconds: 120),
        status: 'OK',
      ),
      MockRfidAntenna(
        name: 'Muck',
        isConnected: true,
        power: -52,
        sensitivity: 0.72,
        heartbeat: Duration(milliseconds: 150),
        status: 'WEAK',
      ),
      MockRfidAntenna(
        name: 'Community',
        isConnected: true,
        power: -38,
        sensitivity: 0.92,
        heartbeat: Duration(milliseconds: 100),
        status: 'OK',
      ),
    ],
    diagnostics: MockDiagnostics(
      signalStrength: -42.0,
      accuracy: 98.5,
      latency: 12.3,
      dropRate: 0.02,
    ),
  );
}

final systemStateProvider =
    StateNotifierProvider<SystemStateNotifier, MockSystemState>(
        (ref) => SystemStateNotifier());
