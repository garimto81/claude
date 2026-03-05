import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/ebs_colors.dart';
import '../../models/mock_system_state.dart';

class DiagnosticPanel extends StatelessWidget {
  final MockDiagnostics diagnostics;

  const DiagnosticPanel({super.key, required this.diagnostics});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _DiagnosticRow(
          label: 'Signal',
          value: '${diagnostics.signalStrength.toStringAsFixed(1)} dBm',
          progress: ((diagnostics.signalStrength + 80) / 80).clamp(0.0, 1.0),
          color: EbsColors.success,
        ),
        const SizedBox(height: 6),
        _DiagnosticRow(
          label: 'Accuracy',
          value: '${diagnostics.accuracy.toStringAsFixed(1)}%',
          progress: diagnostics.accuracy / 100,
          color: EbsColors.accentBlue,
        ),
        const SizedBox(height: 6),
        _DiagnosticRow(
          label: 'Latency',
          value: '${diagnostics.latency.toStringAsFixed(1)}ms',
          progress: (1.0 - diagnostics.latency / 100).clamp(0.0, 1.0),
          color: diagnostics.latency < 20 ? EbsColors.success : EbsColors.warning,
        ),
        const SizedBox(height: 6),
        _DiagnosticRow(
          label: 'Drop Rate',
          value: '${diagnostics.dropRate.toStringAsFixed(2)}%',
          progress: (1.0 - diagnostics.dropRate / 5).clamp(0.0, 1.0),
          color: diagnostics.dropRate < 1 ? EbsColors.success : EbsColors.danger,
        ),
      ],
    );
  }
}

class _DiagnosticRow extends StatelessWidget {
  final String label;
  final String value;
  final double progress;
  final Color color;

  const _DiagnosticRow({
    required this.label,
    required this.value,
    required this.progress,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: 60,
          child: Text(
            label,
            style: const TextStyle(fontSize: 10, color: EbsColors.textMuted),
          ),
        ),
        Expanded(
          child: SizedBox(
            height: 4,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(2),
              child: LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.white.withValues(alpha: 0.08),
                valueColor: AlwaysStoppedAnimation<Color>(color),
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 65,
          child: Text(
            value,
            textAlign: TextAlign.right,
            style: GoogleFonts.jetBrainsMono(
              fontSize: 10,
              color: EbsColors.textSecondary,
            ),
          ),
        ),
      ],
    );
  }
}
