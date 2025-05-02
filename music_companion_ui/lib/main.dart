import 'package:flutter/material.dart';
import 'pages/music_control_page.dart';

void main() => runApp(MusicAssistantApp());

class MusicAssistantApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Music Assistant',
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF1E1E2F),
        primaryColor: const Color(0xFF7C4DFF),
        cardColor: const Color(0xFF2A2A3C),
        sliderTheme: SliderThemeData(
          activeTrackColor: Color(0xFF7C4DFF),
          inactiveTrackColor: Colors.grey.shade700,
          thumbColor: Color(0xFF7C4DFF),
        ),
      ),
      home: MusicControlPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}
