// lib/pages/music_control_page.dart
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:io';
import 'dart:convert';
import '../services/api_service.dart';

class MusicControlPage extends StatefulWidget {
  @override
  _MusicControlPageState createState() => _MusicControlPageState();
}

class _MusicControlPageState extends State<MusicControlPage> {
  String? _audioFilePath;
  List<String> instruments = ['Flute', 'Guitar', 'Pad', 'Bass', 'Keys'];
  Map<String, bool> isEnabled = {};
  Map<String, bool> isMuted = {};
  Map<String, bool> isSolo = {};
  Map<String, double> volumes = {};
  bool isPlaying = false;
  bool isReadyToPlay = false;

  @override
  void initState() {
    super.initState();
    for (var instrument in instruments) {
      isEnabled[instrument] = true;
      isMuted[instrument] = false;
      isSolo[instrument] = false;
      volumes[instrument] = 0.8;
    }
  }

  Future<void> _pickAudioFile() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.audio);
    if (result != null && result.files.single.path != null) {
      setState(() => _audioFilePath = result.files.single.path);

      final file = File(_audioFilePath!);
      final success = await ApiService.analyzeAudio(file);
      if (success) {
        setState(() => isReadyToPlay = true);
      }
    }
  }

  Future<void> _syncVolumeStates() async {
    final Map<String, double> volumesPayload = {
      for (final name in instruments) name: volumes[name]!
    };
    await ApiService.syncVolumes(volumesPayload);
  }

  Future<void> _syncInstrumentStates() async {
    final Map<String, Map<String, dynamic>> controls = {
      for (final name in instruments)
        name: {"mute": isMuted[name], "solo": isSolo[name]},
    };
    await ApiService.syncInstrumentStates(controls);
  }

  void _togglePlayback() async {
    if (!isReadyToPlay) {
      print("⚠️ Please analyze audio first.");
      return;
    }

    await _syncInstrumentStates();
    await _syncVolumeStates();

    setState(() => isPlaying = !isPlaying);
    await (isPlaying ? ApiService.startGeneration() : ApiService.stopGeneration());
  }

  Widget _buildInstrumentControl(String instrument) {
    return AnimatedSwitcher(
      duration: Duration(milliseconds: 400),
      child: Container(
        key: ValueKey(instrument + isPlaying.toString()),
        width: 160,
        margin: const EdgeInsets.symmetric(vertical: 12, horizontal: 10),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [BoxShadow(color: Colors.black54, blurRadius: 6)],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(instrument, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            SizedBox(height: 12),
            Switch(
              value: isEnabled[instrument]!,
              onChanged: (value) => setState(() => isEnabled[instrument] = value),
              activeColor: Colors.greenAccent,
            ),
            SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () => setState(() => isSolo[instrument] = !isSolo[instrument]!),
                  child: Text('S'),
                ),
                ElevatedButton(
                  onPressed: () => setState(() => isMuted[instrument] = !isMuted[instrument]!),
                  child: Text('M'),
                ),
              ],
            ),
            RotatedBox(
              quarterTurns: -1,
              child: Slider(
                value: volumes[instrument]!,
                onChanged: (value) => setState(() => volumes[instrument] = value),
                min: 0,
                max: 1,
                divisions: 20,
                label: '${(volumes[instrument]! * 100).round()}%',
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AnimatedContainer(
        duration: Duration(seconds: 2),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: isPlaying
                ? [Color(0xFF1F1C2C), Color(0xFF928DAB)]
                : [Color(0xFF1E1E2F), Color(0xFF2A2A3C)],
          ),
        ),
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: SingleChildScrollView(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  ElevatedButton.icon(
                    icon: Icon(Icons.upload_file),
                    label: Text("Upload Audio File"),
                    onPressed: _pickAudioFile,
                  ),
                  if (_audioFilePath != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 8.0),
                      child: Text('Selected: ${_audioFilePath!.split("/").last}'),
                    ),
                  SizedBox(height: 24),
                  ElevatedButton.icon(
                    icon: Icon(isPlaying ? Icons.pause : Icons.play_arrow),
                    label: Text(isPlaying ? "Pause" : "Play"),
                    onPressed: isReadyToPlay ? _togglePlayback : null,
                  ),
                  SizedBox(height: 32),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children:
                          instruments.map(_buildInstrumentControl).toList(),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}