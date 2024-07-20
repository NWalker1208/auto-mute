from faster_whisper.transcribe import Segment, Word
from dataclasses import dataclass
import re

@dataclass
class AudioSegment:
  start: float
  end: float

def compile_filters(words: list[str], files: list[str]) -> list[re.Pattern]:
  """Compiles a list of filters from a list of words and filter files."""
  filters = [re.compile(word, re.IGNORECASE) for word in words]
  for file in files:
    filters += _compile_filters_from_file(file)
  return filters

def _compile_filters_from_file(file_path: str) -> list[re.Pattern]:
  """Compiles a list of filters from the lines of a filter file."""
  with open(file_path) as file:
    words = []
    for line in file:
      word = line.rstrip()
      if len(word) > 0 and not word.startswith("#"):
        words.append(re.compile(word, re.IGNORECASE))
    return words

def find_audio_segments_to_filter(transcription_segments: list[Segment], filters: list[re.Pattern], encipher_words: bool) -> list[AudioSegment]:
  """Creates a list of audio segments to filter out based on the provided transcription and filters."""
  words = _flatten_transcription(transcription_segments)
  return _find_filter_segments(words, filters, encipher_words)

def _flatten_transcription(segments: list[Segment]) -> list[Word]:
  """Turns a list of transcription segments into a list of words."""
  return [word for segment in segments for word in segment.words]

def _encipher(s: str) -> str:
  """Enciphers a given string by applying a simple caesar cipher.
  This lets users choose to avoid having profanity in human-readable form."""
  # This array can be modified for other languages.
  ALPHABET = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
  return ''.join([(c if c not in ALPHABET else
                   ALPHABET[(ALPHABET.index(c) + 1) % len(ALPHABET)])
                  for c in s.lower()])

def _matches_any(word: str, filters: list[re.Pattern], encipher_words: bool) -> bool:
  """Checks if the given string matches any pattern from the given list."""
  if encipher_words:
    word = _encipher(word)
  return any(filter.search(word) is not None for filter in filters)

def _find_filter_segments(words: list[Word], filters: list[re.Pattern], encipher_words: bool) -> list[AudioSegment]:
  """Creates a list of audio segments to filter out based on a list of words and filters."""
  return [AudioSegment(word.start, word.end) for word in words
          if _matches_any(word.word, filters, encipher_words)]
