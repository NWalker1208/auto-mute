import ffmpeg
from filters import TimeSegment

# def extract_audio(input_file: str, output_file: str):
#   """Extracts the audio component of the input file at the sample rate required by Whisper."""
#   print("Extracting audio")
#   stream = ffmpeg.input(input_file)
#   stream = ffmpeg.output(stream, output_file, ar=16000, loglevel="warning")
#   # stream = ffmpeg.overwrite_output(stream)
#   ffmpeg.run(stream)

def filter_audio(input_file: str, output_file: str, time_segments_to_mute: list[TimeSegment], padding: tuple[int,int]):
  """Filters the given input file to mute the audio during the provided list of time segments."""
  print("Applying filters")
  stream = ffmpeg.input(input_file)
  video = stream.video
  audio = stream.audio

  start_padding, end_padding = padding
  for s in time_segments_to_mute:
    padded_start = s.start - (start_padding / 1000.0)
    padded_end = s.end + (end_padding / 1000.0)
    audio = ffmpeg.filter(audio, 'volume', volume=0,
                          enable=f"between(t,{padded_start:.3f},{padded_end:.3f})")
  
  stream = ffmpeg.output(video, audio, output_file, vcodec="copy", loglevel="warning")
  # stream = ffmpeg.overwrite_output(stream)
  ffmpeg.run(stream)
  print(f"Saved filtered audio/video file to '{output_file}'")
