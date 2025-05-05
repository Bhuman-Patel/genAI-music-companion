import 'package:flutter/material.dart';
import 'package:music_companion_ui/pages/music_control_page.dart';
import 'package:file_picker/file_picker.dart';
import 'package:lottie/lottie.dart';
import 'dart:html' as html; // For Flutter Web

void main() => runApp(
  const MaterialApp(
    home: MusicControlPage(),
    debugShowCheckedModeBanner: false,
  ),
);

class MusicControlPage extends StatefulWidget {
  const MusicControlPage({super.key});

  @override
  State<MusicControlPage> createState() => _MusicControlPageState();
}

class _MusicControlPageState extends State<MusicControlPage> {
  html.AudioElement? _audioPlayer;
  final List<Map<String, String>> _playbackHistory = [];
  bool _isPlaying = false;
  String? _currentTrack;
  double _volume = 0.5;
  final Map<String, String> _activeMode = {
    'Flute': '',
    'Guitar': '',
    'Pad': '',
    'Bass': '',
    'Keys': '',
  };

  @override
  void initState() {
    super.initState();
    _audioPlayer = html.AudioElement()..volume = _volume;
  }

  void _pickAndPlayAudio() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.audio);
    if (result != null && result.files.single.bytes != null) {
      final file = result.files.single;
      final blob = html.Blob([file.bytes]);
      final url = html.Url.createObjectUrlFromBlob(blob);

      _audioPlayer!.pause();
      _audioPlayer!.src = url;
      _audioPlayer!.load();
      _audioPlayer!.play();

      setState(() {
        _isPlaying = true;
        _currentTrack = file.name;
        _playbackHistory.add({"name": file.name, "url": url});
      });
    }
  }

  void _togglePlay() {
    _audioPlayer?.play();
    setState(() => _isPlaying = true);
  }

  void _togglePause() {
    _audioPlayer?.pause();
    setState(() => _isPlaying = false);
  }

  void _showPlaybackHistory() {
    showDialog(
      context: context,
      builder:
          (_) => AlertDialog(
            backgroundColor: const Color(0xFFF0F0F0), // Soft light gray
            title: const Text("Playback History"),
            content: SizedBox(
              width: 300,
              child:
                  _playbackHistory.isEmpty
                      ? const Text("No files played yet.")
                      : Column(
                        mainAxisSize: MainAxisSize.min,
                        children:
                            _playbackHistory.map((entry) {
                              return ListTile(
                                leading: const Icon(Icons.music_note),
                                title: Text(entry["name"] ?? ""),
                                onTap: () {
                                  _audioPlayer!.pause();
                                  _audioPlayer!.src = entry["url"]!;
                                  _audioPlayer!.load();
                                  _audioPlayer!.play();
                                  setState(() {
                                    _isPlaying = true;
                                    _currentTrack = entry["name"];
                                  });
                                  Navigator.of(context).pop();
                                },
                              );
                            }).toList(),
                      ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text("Close"),
              ),
            ],
          ),
    );
  }

  Widget buildInstrumentCard(String label, String emoji) {
    final isSolo = _activeMode[label] == 'S';
    final isMute = _activeMode[label] == 'M';

    return Container(
      width: 180,
      height: 250,
      margin: const EdgeInsets.all(12),
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade300,
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              const SizedBox(width: 8),
              Text(emoji, style: const TextStyle(fontSize: 22)),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              Tooltip(
                message: 'Solo this instrument',
                child: ElevatedButton(
                  onPressed: () {
                    setState(() {
                      _activeMode[label] = 'S';
                      _audioPlayer?.volume = 1.0;
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor:
                        isSolo ? Colors.grey : Colors.grey.shade100,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: const Text("S"),
                ),
              ),
              Tooltip(
                message: 'Mute this instrument',
                child: ElevatedButton(
                  onPressed: () {
                    setState(() {
                      _activeMode[label] = 'M';
                      _audioPlayer?.volume = 0.0;
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor:
                        isMute ? Colors.grey : Colors.grey.shade100,
                    foregroundColor: Colors.black,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: const Text("M"),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Slider(
            value: _volume,
            onChanged: (value) {
              setState(() {
                _volume = value;
                _audioPlayer?.volume = value;
              });
            },
            min: 0.0,
            max: 1.0,
            activeColor: const Color(0xFFBDBDBD),
            inactiveColor: Colors.grey.shade300,
          ),
          Text(
            "Status: ${isSolo
                ? 'Solo'
                : isMute
                ? 'Mute'
                : 'Active'}",
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 12),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFF8F9FA), Color(0xFFECEFF1)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Column(
              children: [
                const Text(
                  "MindMelody",
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                    fontFamily: 'Poppins',
                  ),
                ),
                const SizedBox(height: 6),
                Image.asset('assets/logo.png', height: 80),
                const SizedBox(height: 6),
                const Text(
                  "Feel the Thought. Hear the Tune.",
                  style: TextStyle(
                    fontSize: 14,
                    color: Color(0xFF607D8B),
                    fontStyle: FontStyle.italic,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                SizedBox(
                  height: 100,
                  child: Lottie.asset(
                    'assets/animations/Melody_flow.json',
                    repeat: true,
                    animate: true,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 30),
            ElevatedButton.icon(
              onPressed: _pickAndPlayAudio,
              icon: const Icon(Icons.upload_file),
              label: const Text("Upload Audio File"),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey.shade200,
                foregroundColor: Colors.black,
                elevation: 0,
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 14,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
              ),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                IconButton(
                  icon: Icon(_isPlaying ? Icons.pause : Icons.play_arrow),
                  tooltip: _isPlaying ? 'Pause' : 'Play',
                  onPressed: () {
                    if (_isPlaying) {
                      _togglePause();
                    } else {
                      _togglePlay();
                    }
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.history),
                  tooltip: 'Playback History',
                  onPressed: _showPlaybackHistory,
                ),
                IconButton(
                  icon: const Icon(Icons.auto_awesome),
                  tooltip: 'Generate Music',
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Music generation triggered! 🎵'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 40),
            Wrap(
              alignment: WrapAlignment.center,
              spacing: 20,
              runSpacing: 20,
              children: [
                buildInstrumentCard("Flute", "🎶"),
                buildInstrumentCard("Guitar", "🎸"),
                buildInstrumentCard("Pad", "🥁"),
                buildInstrumentCard("Bass", "🎷"),
                buildInstrumentCard("Keys", "🎹"),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
