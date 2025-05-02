// lib/services/api_service.dart
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:5000';

  static Future<bool> analyzeAudio(File file) async {
    final uri = Uri.parse('$baseUrl/analyze-audio');
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('file', file.path));

    final response = await request.send();
    final body = await response.stream.bytesToString();
    print("📤 Analyze Audio Response: $body");
    return response.statusCode == 200 && body.contains('json_result');
  }

  static Future<void> syncVolumes(Map<String, double> volumes) async {
    final uri = Uri.parse('$baseUrl/update-volumes');
    final response = await http.post(uri,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"volumes": volumes}));
    print("🔊 Volume sync: ${response.body}");
  }

  static Future<void> syncInstrumentStates(Map<String, Map<String, dynamic>> states) async {
    final uri = Uri.parse('$baseUrl/update-controls');
    final response = await http.post(uri,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"instrument_states": states}));
    print("🎛 Instrument state sync: ${response.body}");
  }

  static Future<void> startGeneration() async {
    final uri = Uri.parse('$baseUrl/start-generation');
    final response = await http.post(uri);
    print("▶️ Start: ${response.body}");
  }

  static Future<void> stopGeneration() async {
    final uri = Uri.parse('$baseUrl/stop-generation');
    final response = await http.post(uri);
    print("⏹ Stop: ${response.body}");
  }
}