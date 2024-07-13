import ffmpeg
import whisper
import numpy
import re
from dataclasses import dataclass
from typing import Iterator

def extract_audio(input_file: str, output_file: str):
  stream = ffmpeg.input(input_file)
  stream = ffmpeg.output(stream, output_file, ar=16000)
  stream = ffmpeg.overwrite_output(stream)
  ffmpeg.run(stream)

def transcribe_audio(input_file: str, model_name: str = "small.en") -> dict[str, str | list]:
  model = whisper.load_model(model_name)
  transcript = model.transcribe(
    audio=input_file,
    word_timestamps=True,
    verbose=False
  )
  return transcript

@dataclass
class WordTimestamp:
  """Class representing the timestamp of a specific word in a piece of audio."""
  word: str
  start: numpy.float64
  end: numpy.float64

def get_word_timestamps(transcript: dict[str, str | list]) -> Iterator[WordTimestamp]:
  for segment in transcript['segments']:
    for word in segment['words']:
      yield WordTimestamp(word['word'], word['start'], word['end'])

def filter_words(words: list[WordTimestamp], filters: list[re.Pattern]) -> Iterator[WordTimestamp]:
  for word in words:
    for filter in filters:
      if filter.search(word.word) is not None:
        yield word
        break

def filter_audio(input_file: str, output_file: str, words_to_remove: list[WordTimestamp]):
  stream = ffmpeg.input(input_file)
  video = stream.video
  audio = stream.audio

  for word in words_to_remove:
    audio = ffmpeg.filter(audio, 'volume', volume=0,
                          enable=f"between(t,{word.start:.3f},{word.end:.3f})")
  
  stream = ffmpeg.output(video, audio, output_file, vcodec="copy")
  stream = ffmpeg.overwrite_output(stream)
  ffmpeg.run(stream)

def main():
  extract_audio("video.mp4", "audio.wav")
  transcript = transcribe_audio("audio.wav")
  words = list(get_word_timestamps(transcript))
  filters = [re.compile("missile", re.IGNORECASE)]
  filtered_words = list(filter_words(words, filters))
  filter_audio("video.mp4", "filtered-video.mp4", filtered_words)

if __name__ == "__main__":
  main()
