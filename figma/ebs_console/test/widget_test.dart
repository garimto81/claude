import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ebs_console/app.dart';

void main() {
  testWidgets('EBS Console app renders', (WidgetTester tester) async {
    // Set screen size to 1920x1080 (target resolution)
    tester.view.physicalSize = const Size(1920, 1080);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const ProviderScope(child: EbsApp()));
    expect(find.text('E B S'), findsOneWidget);
  });
}
