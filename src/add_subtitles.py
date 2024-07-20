import transcription

def seconds_to_ts(seconds: float) -> str:
  milliseconds = round(seconds * 1000)
  seconds = milliseconds // 1000
  minutes = seconds // 60
  hours = minutes // 60
  milliseconds %= 1000
  seconds %= 60
  minutes %= 60
  return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

segments = transcription.transcribe("./media/missile.mp4", "small.en", whisper_kwargs={
    "compute_type": "auto",
    "device": "auto"
  },
  transcribe_kwargs={
    "vad_filter": False,
    "vad_parameters": {}
  }
)

with open('subtitles.srt', 'w') as file:
  i = 1
  for segment in segments:
    start = seconds_to_ts(segment.start)
    end = seconds_to_ts(segment.end)
    file.write(f"{i}\n")
    file.write(f"{start} --> {end}\n")
    file.write(f"{segment.text.strip()}\n")
    file.write("\n")
    i += 1

# TODO: https://www.bannerbear.com/blog/how-to-add-subtitles-to-a-video-file-using-ffmpeg/#hard-subtitles-vs-soft-subtitles
