import 'package:flutter/material.dart';

class MockRfidAntenna {
  final String name;
  final bool isConnected;
  final int power;
  final double sensitivity;
  final Duration heartbeat;
  final String status;

  const MockRfidAntenna({
    required this.name,
    required this.isConnected,
    required this.power,
    required this.sensitivity,
    required this.heartbeat,
    required this.status,
  });

  MockRfidAntenna copyWith({
    String? name,
    bool? isConnected,
    int? power,
    double? sensitivity,
    Duration? heartbeat,
    String? status,
  }) {
    return MockRfidAntenna(
      name: name ?? this.name,
      isConnected: isConnected ?? this.isConnected,
      power: power ?? this.power,
      sensitivity: sensitivity ?? this.sensitivity,
      heartbeat: heartbeat ?? this.heartbeat,
      status: status ?? this.status,
    );
  }
}

class MockDiagnostics {
  final double signalStrength;
  final double accuracy;
  final double latency;
  final double dropRate;

  const MockDiagnostics({
    required this.signalStrength,
    required this.accuracy,
    required this.latency,
    required this.dropRate,
  });

  MockDiagnostics copyWith({
    double? signalStrength,
    double? accuracy,
    double? latency,
    double? dropRate,
  }) {
    return MockDiagnostics(
      signalStrength: signalStrength ?? this.signalStrength,
      accuracy: accuracy ?? this.accuracy,
      latency: latency ?? this.latency,
      dropRate: dropRate ?? this.dropRate,
    );
  }
}

class MockSystemState {
  final bool rfidConnected;
  final bool atConnected;
  final bool engineOk;
  final double cpuUsage;
  final double gpuUsage;
  final double memUsage;
  final String cameraMode;
  final bool chromaKeyEnabled;
  final Color chromaKeyColor;
  final List<MockRfidAntenna> antennas;
  final MockDiagnostics diagnostics;

  const MockSystemState({
    required this.rfidConnected,
    required this.atConnected,
    required this.engineOk,
    required this.cpuUsage,
    required this.gpuUsage,
    required this.memUsage,
    required this.cameraMode,
    required this.chromaKeyEnabled,
    required this.chromaKeyColor,
    required this.antennas,
    required this.diagnostics,
  });

  MockSystemState copyWith({
    bool? rfidConnected,
    bool? atConnected,
    bool? engineOk,
    double? cpuUsage,
    double? gpuUsage,
    double? memUsage,
    String? cameraMode,
    bool? chromaKeyEnabled,
    Color? chromaKeyColor,
    List<MockRfidAntenna>? antennas,
    MockDiagnostics? diagnostics,
  }) {
    return MockSystemState(
      rfidConnected: rfidConnected ?? this.rfidConnected,
      atConnected: atConnected ?? this.atConnected,
      engineOk: engineOk ?? this.engineOk,
      cpuUsage: cpuUsage ?? this.cpuUsage,
      gpuUsage: gpuUsage ?? this.gpuUsage,
      memUsage: memUsage ?? this.memUsage,
      cameraMode: cameraMode ?? this.cameraMode,
      chromaKeyEnabled: chromaKeyEnabled ?? this.chromaKeyEnabled,
      chromaKeyColor: chromaKeyColor ?? this.chromaKeyColor,
      antennas: antennas ?? this.antennas,
      diagnostics: diagnostics ?? this.diagnostics,
    );
  }
}
