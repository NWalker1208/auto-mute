from faster_whisper.transcribe import Segment, Word
import re
import transcription
from filters import compile_filters, filter_text

def seconds_to_ts(seconds: float) -> str:
  centiseconds = round(seconds * 100)
  seconds = centiseconds // 100
  minutes = seconds // 60
  hours = minutes // 60
  centiseconds %= 100
  seconds %= 60
  minutes %= 60
  return f"{hours:01}:{minutes:02}:{seconds:02}.{centiseconds:02}"

def layout_subtitles(segments: list[Segment]) -> list[list[Word]]:
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
  subtitle_char_count = 0
  subtitle = []
  for sentence in sentences:
    for word in sentence:
      subtitle.append(word)
      subtitle_char_count += len(word.word)

      if subtitle_char_count > 80:
        # TODO: Find smarter place to split long sentences
        subtitles.append(subtitle)
        subtitle = []
        subtitle_char_count = 0
    
    if len(subtitle) > 0:
      subtitles.append(subtitle)
      subtitle = []
      subtitle_char_count = 0

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

FILE_HEADER = \
"""[Script Info]
; Script generated by automute
ScriptType: v4.00+
PlayResX: 480
PlayResY: 360
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,18,&Hffffff,&H00ffff,&H000000,&H80000000,0,0,0,0,100,100,0,0,1,1,1,2,10,10,10,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
LINE_FORMAT = "Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"
WORD_FORMAT = "{{\\1a&H{alpha:02X}&}}{text}{{\\1a}}"

# SRT does not seem to support font opacity, only color.
# mov_text (i.e., mp4) does not seem to support font color at all.
# Only SubStation Alpha seems to support opacity.
# It seems like ffmpeg likes to have all of the possible fields present, at least when converting from SSA to SRT.
def write_subtitles(subtitles: list[list[Word]], path: str):
  with open(path, 'w') as file:
    file.write(FILE_HEADER)
    for subtitle in subtitles:
      start = seconds_to_ts(subtitle[0].start)
      end = seconds_to_ts(subtitle[-1].end)
      text = ""
      first = True
      for word in subtitle:
        word_text = word.word
        if first:
          word_text = word_text.lstrip()
          first = False
        text += WORD_FORMAT.format(alpha=probability_to_alpha(word.probability), text=word_text)
      file.write(LINE_FORMAT.format(start=start, end=end, text=text.strip()))

def probability_to_alpha(probability: float) -> int:
  MIN_ALPHA = 0x00
  MAX_ALPHA = 0xA0
  MIN_PROBABILITY = 0.2
  MAX_PROBABILITY = 0.9
  lerp = 1.0 - min(max((probability - MIN_PROBABILITY) / (MAX_PROBABILITY - MIN_PROBABILITY), 0.0), 1.0)
  return MIN_ALPHA + int(lerp * (MAX_ALPHA - MIN_ALPHA))

def filter_subtitles(subtitles: list[list[Word]], filters: list[re.Pattern], replacement: str, encipher_text: bool) -> list[list[Word]]:
  new_subtitles = []
  for subtitle in subtitles:
    new_words = []
    for word in subtitle:
      new_words.append(Word(word.start, word.end, filter_text(word.word, filters, replacement, encipher_text), word.probability))
    new_subtitles.append(new_words)
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
  subtitles = filter_subtitles(subtitles, filter_list, '[__]', True)
  write_subtitles(subtitles, "./media/subtitles.ssa")

  # TODO: https://www.bannerbear.com/blog/how-to-add-subtitles-to-a-video-file-using-ffmpeg/#hard-subtitles-vs-soft-subtitles

if __name__ == "__main__":
  main()
