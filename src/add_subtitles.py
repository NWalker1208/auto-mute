from faster_whisper.transcribe import Segment, Word
from dataclasses import dataclass
import re
import transcription
from filters import compile_filters

def seconds_to_ts(seconds: float) -> str:
  milliseconds = round(seconds * 1000)
  seconds = milliseconds // 1000
  minutes = seconds // 60
  hours = minutes // 60
  milliseconds %= 1000
  seconds %= 60
  minutes %= 60
  return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

@dataclass
class Subtitle:
  start: float
  end: float
  lines: list[str]

def layout_subtitles(segments: list[Segment]) -> list[Subtitle]:
  """Transforms a list of transcription segments into a list of subtitles."""
  # Conventions to follow: https://engagemedia.org/help/best-practices-for-online-subtitling/
  # - Max = 2 lines
  # - In general, appear and disappear with timing of spoken text.
  # - Minimum time = max(1.5 seconds, long enough to read), unless next line needs to appear sooner.
  # - If a line is repeated, insert a blank gap between the repeats.
  # - Separate subtitle for each sentence, except for very short sentences.
  # - Prefer line break on punctuation.
  # More conventions: https://diposit.ub.edu/dspace/bitstream/2445/128428/1/subtitling%20and%20captioning.pdf
  # - 40 characters per line
  # - >=1.5, <=6 seconds per subtitle
  # - 0.125 second gap between subtitles
  words = [word for segment in segments for word in segment.words]
  sentences = group_sentences(words)
  subtitles = []
  # TODO: Incorporate conventions above.
  for sentence in sentences:
    text = ''.join(w.word for w in sentence).strip()
    start = sentence[0].start
    end = sentence[-1].end
    subtitles.append(Subtitle(start, end, [text]))
  return subtitles

def group_sentences(words: list[Word]) -> list[list[Word]]:
  """Groups words from a list into sentences based on punctuation."""
  sentences = []
  current_sentence = []
  for word in words:
    current_sentence.append(word)
    text = word.word
    if text.endswith('.') or text.endswith('!') or text.endswith('?'):
      sentences.append(current_sentence)
      current_sentence = []
  if len(current_sentence) > 0:
    sentences.append(current_sentence)
  return sentences

def write_subtitles(subtitles: list[Subtitle], path: str):
  with open(path, 'w') as file:
    i = 1
    for subtitle in subtitles:
      start = seconds_to_ts(subtitle.start)
      end = seconds_to_ts(subtitle.end)
      file.write(f"{i}\n")
      file.write(f"{start} --> {end}\n")
      for line in subtitle.lines:
        file.write(f"{line}\n")
      file.write("\n")
      i += 1

def filter_subtitles(subtitles: list[Subtitle], filters: list[re.Pattern], replacement: str) -> list[Subtitle]:
  new_subtitles = []
  for subtitle in subtitles:
    new_lines = []
    for line in subtitle.lines:
      new_line = line
      for filter in filters:
        new_line = filter.sub(replacement, new_line)
      new_lines.append(new_line)
    new_subtitles.append(Subtitle(subtitle.start, subtitle.end, new_lines))
  return new_subtitles

def main():
  segments = transcription.transcribe("./media/missile.mp4", "small.en", whisper_kwargs={
      "compute_type": "auto",
      "device": "auto"
    },
    transcribe_kwargs={
      "vad_filter": False,
      "vad_parameters": {}
    }
  )
  subtitles = layout_subtitles(segments)
  filter_list = compile_filters([], ['default_wordlist_en.txt'])
  subtitles = filter_subtitles(subtitles, filter_list, '[__]')
  write_subtitles(subtitles, "./media/subtitles.srt")

  # TODO: https://www.bannerbear.com/blog/how-to-add-subtitles-to-a-video-file-using-ffmpeg/#hard-subtitles-vs-soft-subtitles

if __name__ == "__main__":
  main()
