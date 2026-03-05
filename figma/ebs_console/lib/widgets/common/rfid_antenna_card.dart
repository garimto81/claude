import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../theme/ebs_colors.dart';
import '../../models/mock_system_state.dart';

class RfidAntennaCard extends StatelessWidget {
  final MockRfidAntenna antenna;

  const RfidAntennaCard({super.key, required this.antenna});

  @override
  Widget build(BuildContext context) {
    final statusColor = switch (antenna.status) {
      'OK' => EbsColors.success,
      'WEAK' => EbsColors.warning,
      _ => EbsColors.danger,
    };

    return Container(
      padding: const EdgeInsets.all(EbsColors.spacingSm),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.04),
        border: Border.all(color: EbsColors.glassBorder),
        borderRadius: BorderRadius.circular(EbsColors.borderRadius),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: name + status
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: statusColor,
                  boxShadow: [BoxShadow(color: statusColor.withValues(alpha: 0.6), blurRadius: 6)],
                ),
              ),
              const SizedBox(width: 8),
              Text(
                antenna.name,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: EbsColors.textPrimary,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.15),
                  border: Border.all(color: statusColor.withValues(alpha: 0.3)),
                  borderRadius: BorderRadius.circular(3),
                ),
                child: Text(
                  antenna.status,
                  style: TextStyle(
                    fontSize: 9,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.5,
                    color: statusColor,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // Metrics
          _Metric('Power', '${antenna.power} dBm'),
          _Metric('Sensitivity', antenna.sensitivity.toStringAsFixed(2)),
          _Metric('Heartbeat', '${antenna.heartbeat.inMilliseconds}ms'),
        ],
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  final String label;
  final String value;
  const _Metric(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 10, color: EbsColors.textMuted),
          ),
          const Spacer(),
          Text(
            value,
            style: GoogleFonts.jetBrainsMono(
              fontSize: 10,
              color: EbsColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}
