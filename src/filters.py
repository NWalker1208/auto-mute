from faster_whisper.transcribe import Segment, Word
from dataclasses import dataclass
import re

@dataclass
class TimeSegment:
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
        words.append(re.compile(f'\\b{word}\\b', re.IGNORECASE))
    return words

def find_time_segments_to_filter(transcription_segments: list[Segment], filters: list[re.Pattern], encipher_words: bool) -> list[TimeSegment]:
  """Creates a list of audio segments to filter out based on the provided transcription and filters."""
  words = _flatten_transcription(transcription_segments)
  return _find_filter_segments(words, filters, encipher_words)

def _flatten_transcription(segments: list[Segment]) -> list[Word]:
  """Turns a list of transcription segments into a list of words."""
  return [word for segment in segments for word in segment.words]

def filter_transcription(transcription_segments: list[Segment], filters: list[re.Pattern], replacement_text: str, encipher_text: bool) -> tuple[list[Segment], int]:
  """
  Applies the list of filters to a transcription, replacing any matches with the given replacement string.
  Returns the filtered transcription and the number of matches that were found.
  """
  new_segments = []
  total_matches = 0
  for segment in transcription_segments:
    new_words = []
    for word in segment.words:
      filtered_word, matches = _filter_text(word.word, filters, replacement_text, encipher_text)
      total_matches += matches
      new_words.append(Word(
        start=word.start,
        end=word.end,
        word=filtered_word,
        probability=word.probability
      ))
    new_segments.append(Segment(
      id=segment.id,
      seek=segment.seek,
      start=segment.start,
      end=segment.end,
      text=''.join(w.text for w in new_words),
      tokens=segment.tokens,
      temperature=segment.temperature,
      avg_logprob=segment.avg_logprob,
      compression_ratio=segment.compression_ratio,
      no_speech_prob=segment.no_speech_prob,
      words=new_words
    ))
  return new_segments, total_matches

# This array can be modified for other languages.
_ALPHABET = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def _shift_letter(c: str, offset: int) -> str:
  """Rotates a character through the alphabet, if it is a letter."""
  c_lower = c.lower()
  if c_lower not in _ALPHABET:
    return c
  
  o_lower = _ALPHABET[(_ALPHABET.index(c_lower) + offset) % len(_ALPHABET)]
  return o_lower if c.islower() else o_lower.upper()

def _encipher(s: str) -> str:
  """Enciphers a given string by applying a simple caesar cipher.
  This lets users choose to avoid having profanity in human-readable form."""
  return ''.join(_shift_letter(c, 1) for c in s)

def _decipher(s: str) -> str:
  """The inverse of _encipher."""
  return ''.join(_shift_letter(c, -1) for c in s)

def _matches_any(word: str, filters: list[re.Pattern], encipher_words: bool) -> bool:
  """Checks if the given string matches any pattern from the given list."""
  if encipher_words:
    word = _encipher(word)
  return any(filter.search(word) is not None for filter in filters)

def _find_filter_segments(words: list[Word], filters: list[re.Pattern], encipher_words: bool) -> list[AudioSegment]:
  """Creates a list of audio segments to filter out based on a list of words and filters."""
  return [AudioSegment(word.start, word.end) for word in words
          if _matches_any(word.word, filters, encipher_words)]

def _filter_text(text: str, filters: list[re.Pattern], replacement_text: str, encipher_text: bool) -> tuple[str, int]:
  """
  Applies the list of filters to a string, replacing any matches with the given replacement string.
  Returns the filtered string and the number of matches that were found.
  """
  if encipher_text:
    text = _encipher(text)
    replacement_text = _encipher(replacement_text)
  total_matches = 0
  for filter in filters:
    matches = len(filter.findall(text))
    if matches > 0:
      text = filter.sub(replacement_text, text)
      total_matches += matches
  if encipher_text:
    text = _decipher(text)
  return text, total_matches
