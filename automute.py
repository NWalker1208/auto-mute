import ffmpeg
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment, Word
import re

def extract_audio(input_file: str, output_file: str):
  """Extracts the audio component of the input file at the sample rate required by Whisper."""
  stream = ffmpeg.input(input_file)
  stream = ffmpeg.output(stream, output_file, ar=16000)
  stream = ffmpeg.overwrite_output(stream)
  ffmpeg.run(stream)

def transcribe_audio(input_file: str, model_name: str = "small.en") -> list[Segment]:
  """Feeds the audio file into the specified Whisper model and returns the transcribed segments."""
  model = WhisperModel(
    model_size_or_path = model_name,
    compute_type = "float32"
  )
  segments, _ = model.transcribe(
    audio = input_file,
    word_timestamps = True
  )
  return list(segments)

def get_words(segments: list[Segment]) -> list[Word]:
  """Flattens a list of transcription segments into a list of transcribed words."""
  return [word for segment in segments for word in segment.words]

def matches_any(s: str, filters: list[re.Pattern]) -> bool:
  """Checks if the given string matches any pattern from the given list."""
  for filter in filters:
    if filter.search(s) is not None:
      return True
  return False

def filter_words(words: list[Word], filters: list[re.Pattern]) -> list[Word]:
  """Filters the given list of words to only those matching at least one of the given filters."""
  return [word for word in words if matches_any(word.word, filters)]

def filter_audio(input_file: str, output_file: str, words_to_remove: list[Word]):
  """Filters the audio component of the given input file to mute the provided list of transcribed words."""
  stream = ffmpeg.input(input_file)
  video = stream.video
  audio = stream.audio

  for word in words_to_remove:
    audio = ffmpeg.filter(audio, 'volume', volume=0,
                          enable=f"between(t,{word.start:.3f},{word.end:.3f})")
  
  stream = ffmpeg.output(video, audio, output_file, vcodec="copy")
  stream = ffmpeg.overwrite_output(stream)
  ffmpeg.run(stream)

FILTERS = [
  re.compile("missile", re.IGNORECASE)
]

def main():
  extract_audio("video.mp4", "audio.wav")
  segments = transcribe_audio("audio.wav")
  words = get_words(segments)
  filtered_words = filter_words(words, FILTERS)
  filter_audio("video.mp4", "filtered-video.mp4", filtered_words)

if __name__ == "__main__":
  main()
