package com.nwalker1208.automute;

import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Pattern;

import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;

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

    System.out.println("Parsing CSV transcription...");
    TranscriptionLine[] transcription = ReadCsv("transcription.csv");
    if (transcription == null) {
      System.err.println("Failed to read CSV file.");
      return;
    }

    System.out.printf("Found %d lines of text.\n", transcription.length);
    TranscriptionLine[] linesToFilter = FindLinesToFilter(transcription);
    System.out.printf("%d lines match filters.\n", linesToFilter.length);
    
    System.out.println("Filtering audio from input file...");
    if (!FilterAudio("video.mp4", linesToFilter)) {
      System.err.println("Failed to filter input file.");
      return;
    }

    System.out.println("Finished");
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
        "lib/whisper.cpp/main", "-m", "model.bin", "-ml", "1", "-ocsv", "-of", "transcription", inputFile
      );
      builder.inheritIO();
      Process p = builder.start();
      return p.waitFor() == 0;
    } catch (IOException | InterruptedException e) {
      return false;
    }
  }

  public static TranscriptionLine[] ReadCsv(String transcriptionCsvFile) {
    List<TranscriptionLine> lines = new ArrayList<>();
    try (CSVReader reader = new CSVReader(new FileReader(transcriptionCsvFile))) {
      String[] values = null;
      // Skip header row
      reader.readNext();
      // Read remaining rows
      while ((values = reader.readNext()) != null) {
        if (values.length != 3) {
          System.err.println("Whisper generated a malformed CSV file. Expected to find 3 values per row.");
          return null;
        }
        try {
          long startMs = Long.parseLong(values[0]);
          long endMs = Long.parseLong(values[1]);
          String text = values[2];
          lines.add(new TranscriptionLine(startMs, endMs, text));
        } catch (NumberFormatException e) {
          System.err.println("Whisper generated a malformed CSV file. Expected to find integers in the first two columns.");
          return null;
        }
      }
    } catch (CsvValidationException e) {
      System.err.println("Whisper generated a malformed CSV file. " + e.getMessage());
      return null;
    } catch (IOException e) {
      System.err.println("Error while attempting to read CSV file: " + e.getMessage());
      return null;
    }
    return lines.toArray(new TranscriptionLine[lines.size()]);
  }

  public static Pattern[] filters = {
    Pattern.compile("missile", Pattern.CASE_INSENSITIVE)
  };

  public static TranscriptionLine[] FindLinesToFilter(TranscriptionLine[] lines) {
    List<TranscriptionLine> linesToFilter = new ArrayList<>();
    for (TranscriptionLine line : lines) {
      for (Pattern pattern : filters) {
        if (pattern.matcher(line.text).find()) {
          linesToFilter.add(line);
          break;
        }
      }
    }
    return linesToFilter.toArray(new TranscriptionLine[linesToFilter.size()]);
  }

  public static boolean FilterAudio(String inputFile, TranscriptionLine[] linesToFilter) {
    return false;
  }
}

class TranscriptionLine {
  public final long startMs;
  public final long endMs;
  public final String text;

  public TranscriptionLine(long startMs, long endMs, String text) {
    this.startMs = startMs;
    this.endMs = endMs;
    this.text = text;
  }
}
