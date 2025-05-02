import 'package:file_picker/file_picker.dart';
import 'dart:io';

class FileHelper {
  static Future<File?> pickAudioFile() async {
    final result = await FilePicker.platform.pickFiles(type: FileType.audio);
    if (result != null && result.files.single.path != null) {
      return File(result.files.single.path!);
    }
    return null;
  }
}
