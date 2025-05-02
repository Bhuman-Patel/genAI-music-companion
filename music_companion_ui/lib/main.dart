import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;


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
}

Future<void> _pickAudioFile() async {
final result = await FilePicker.platform.pickFiles(type: FileType.custom, allowedExtensions: ['wav']);
if (result != null && result.files.single.path != null) {
  setState(() {
    _audioFilePath = result.files.single.path;
  });

  final file = File(_audioFilePath!);
  final uri = Uri.parse('http://127.0.0.1:5000/analyze-audio');
  final request = http.MultipartRequest('POST', uri);
  request.files.add(await http.MultipartFile.fromPath('file', file.path));

  final response = await request.send();
  final responseBody = await response.stream.bytesToString();

  if (response.statusCode == 200) {
    final decoded = jsonDecode(responseBody);
    print("✅ Audio features received: ${decoded["json_result"]}");
  } else {
    print("❌ Upload failed: ${response.statusCode}");
  }
}
}  


void _togglePlayback() async {
setState(() {
  isPlaying = !isPlaying;
});

final uri = Uri.parse(isPlaying
    ? 'http://127.0.0.1:5000/start-generation'
    : 'http://127.0.0.1:5000/stop-generation');

final response = await http.post(uri);
print(response.body);
}



Widget _buildInstrumentControl(String instrument) {
  return AnimatedSwitcher(
    duration: Duration(milliseconds: 400),
    transitionBuilder: (child, animation) => FadeTransition(
      opacity: animation,
      child: ScaleTransition(scale: animation, child: child),
    ),
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
                child: Text('S', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: isSolo[instrument]! ? Colors.yellowAccent : Colors.grey.shade700,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                  padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                ),
              ),
              ElevatedButton(
                onPressed: () => setState(() => isMuted[instrument] = !isMuted[instrument]!),
                child: Text('M', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: isMuted[instrument]! ? Colors.redAccent : Colors.grey.shade700,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
                  padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                ),
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
      curve: Curves.easeInOut,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: isPlaying
              ? [Color(0xFF1F1C2C), Color(0xFF928DAB)]  // Vibrant and visible
              : [Color(0xFF1E1E2F), Color(0xFF2A2A3C)], // Default DAW-like
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
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Theme.of(context).primaryColor,
                    padding: EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                    textStyle: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  onPressed: _pickAudioFile,
                ),
                if (_audioFilePath != null) ...[
                  SizedBox(height: 16),
                  Text(
                    'Selected: ${_audioFilePath!.split("/").last}',
                    style: TextStyle(fontSize: 16, color: Colors.white70),
                  ),
                ],
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  icon: Icon(isPlaying ? Icons.pause : Icons.play_arrow),
                  label: Text(isPlaying ? "Pause" : "Play"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.lightGreenAccent,
                    foregroundColor: Colors.black,
                    padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                    textStyle: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  onPressed: _togglePlayback,
                ),
                const SizedBox(height: 40),
                SizedBox(height: 20),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: AnimatedSwitcher(
                    duration: Duration(milliseconds: 500),
                    transitionBuilder: (child, animation) =>
                        ScaleTransition(scale: animation, child: child),
                    child: Row(
                      key: ValueKey(isPlaying),
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: instruments.map(_buildInstrumentControl).toList(),
                    ),
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
