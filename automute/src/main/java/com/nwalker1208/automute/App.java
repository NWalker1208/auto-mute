package com.nwalker1208.automute;

import java.io.IOException;

public class App {
  public static void main(String[] args) {
    System.out.println("Extracting audio...");
    if (!ExtractAudio("video.mp4")) {
      System.err.println("Failed to extract audio.");
      return;
    }
    System.out.println("Transcribing audio...");
    if (!CallWhisper("audio.wav")) {
      System.err.println("Failed to extract audio.");
      return;
    }
  }

  public static boolean ExtractAudio(String inputFile) {
    try {
      ProcessBuilder builder = new ProcessBuilder(
        "ffmpeg", "-y", "-i", inputFile, "-ar", "16000", "audio.wav"
      );
      builder.inheritIO();
      Process p = builder.start();
      return p.waitFor() == 0;
    } catch (IOException | InterruptedException e) {
      return false;
    }
  }

  public static boolean CallWhisper(String inputFile) {
    try {
      ProcessBuilder builder = new ProcessBuilder(
        "lib/whisper.cpp/main", "-m", "model.bin", "-ml", "1", inputFile
      );
      builder.inheritIO();
      Process p = builder.start();
      return p.waitFor() == 0;
    } catch (IOException | InterruptedException e) {
      return false;
    }
  }
}
