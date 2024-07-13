import ffmpeg
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment, Word
from tqdm import tqdm
import argparse, re, os, pathlib

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
  segments, info = model.transcribe(
    audio = input_file,
    word_timestamps = True
  )
  total_duration = round(info.duration, 2)

  # https://github.com/SYSTRAN/faster-whisper/issues/80#issuecomment-1502174272
  segments_list = []
  with tqdm(desc="Transcribing audio", total=total_duration, unit=" seconds") as progress:
    for segment in segments:
      progress.update(segment.end - progress.n)
      segments_list.append(segment)
    progress.update(total_duration - progress.n)

  return segments_list

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

def get_output_file_path(input_file: str) -> str:
  """Creates an output file path from an input file path."""
  input_path = pathlib.Path(input_file)
  return str(input_path.with_stem(input_path.stem + "-filtered"))

def main():
  parser = argparse.ArgumentParser(
    prog='automute',
    description='A command-line tool for automatically muting specific words from audio and video files.'
  )
  parser.add_argument('input-file',
                      help='Audio or video file to apply filters to.')
  parser.add_argument('-o', '--output',
                      help='Name of the output file. (Default: <input file>-filtered.<extension>)')
  parser.add_argument('-w', '--filter-word', default=[], action='append',
                      help="A word to filter out. Treated as a case-insensitive regular expression. Can be specified multiple times.")
  # parser.add_argument('-l', '--filter-lines',
  #                     help="A file of words to filter out. Each line is treated as a case-insentive regular expression.")
  args = parser.parse_args()
  
  input_file = args.input_file
  output_file = args.output if args.output is not None else get_output_file_path(input_file)
  filters = [re.compile(word, re.IGNORECASE) for word in args.filter_word]

  extract_audio(input_file, "audio.wav")
  segments = transcribe_audio("audio.wav")
  os.remove("audio.wav")

  words = get_words(segments)
  filtered_words = filter_words(words, filters)
  filter_audio(input_file, output_file, filtered_words)

if __name__ == "__main__":
  main()
