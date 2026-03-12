import 'package:flutter/material.dart';
import 'theme/ebs_theme.dart';
import 'screens/console_screen.dart';

class EbsApp extends StatelessWidget {
  const EbsApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EBS Console',
      debugShowCheckedModeBanner: false,
      theme: EbsTheme.dark,
      home: const ConsoleScreen(),
    );
  }
}
