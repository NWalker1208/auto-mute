import argparse, pathlib
from cli import confirm

def _parse_arguments() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    prog='automute',
    description='A command-line tool for automatically muting specific words from audio and video files.'
  )
  parser.add_argument('input',
                      help='Audio or video file to apply filters to.')
  parser.add_argument('-o', '--output',
                      help='Name of the output file. (Default: <input file>-filtered.<extension>)')
  parser.add_argument('-w', '--filter-word', default=[], action='append',
                      help='A word to filter out. Treated as a case-insensitive regular expression. Can be specified multiple times.')
  parser.add_argument('-f', '--filter-file', default=[], action='append',
                      help="A file of words to filter out. Each line is treated as a case-insentive regular expression.")
  parser.add_argument('-e', '--encipher-words', default=False, action='store_true',
                      help='Before applying filters, enchiper transcribed words by replacing each letter with the one immediately after it in the alphabet ' +
                           '(looping around at the end; i.e., caesar cipher with a shift of 1). Use this if you need to filter out profanity but would prefer ' +
                           'not to read profanity when specifying your filters.')
  parser.add_argument('-p', '--padding', default=(0,0), type=_parse_padding, 
                      help='Padding in milliseconds to apply around filtered audio segments. Can be specified as a single integer or as two integers separated ' +
                           'by a comma to specify the start and end padding separately. (Default: 0)')
  parser.add_argument('--whisper-model', default='small.en',
                      help='The faster_whisper model to use for audio transcription. Can be a model name (tiny, tiny.en, base, base.en, small, small.en, ' +
                           'distil-small.en, medium, medium.en, distil-medium.en, large, large-v1, large-v2, distil-large-v2, large-v3, or distil-large-v3), ' +
                           'a CTranslate2-converted model ID from Hugging Face, or a path to a local model. See faster-whisper docs. (Default: small.en)')
  parser.add_argument('--whisper-compute-type', default='auto', choices=['default','auto','int8','int8_float16','int8_bfloat16','int8_float32','int16','float16','bfloat16','float32'],
                      help='The compute type to use when loading the Whisper model. \'default\' explicitly uses the same quantization that the model is already using. ' + 
                           '\'auto\' selects the fasted option that is supported by the device used. (Default: auto)')
  parser.add_argument('--whisper-device', default='auto', choices=['auto','cpu','cuda'],
                      help='The compute device to use when running the Whisper model. (Default: auto)')
  # parser.add_argument('--whisper-silence-ms', default=-1, type=int,
  #                     help='The minimum duration in milliseconds for an audio segment with no detected speech to be skipped during transcription. -1 to disable. ' +
  #                          '(Default: -1)')
  parser.add_argument('--ignore-cached-transcriptions', default=False, action='store_true',
                      help='Ignore any cached transcriptions.')
  return parser.parse_args()

def _parse_padding(padding_str: str) -> tuple[int,int]:
  """Parses a padding tuple from a string of one or two integers."""
  values = [int(x) for x in padding_str.split(',')]
  if len(values) == 1:
    return (values[0], values[0])
  elif len(values) == 2:
    return (values[0], values[1])
  else:
    raise argparse.ArgumentTypeError(f"{padding_str} is not a valid padding value")

def _get_output_file_path(input_file: str) -> str:
  """Creates an output file path from an input file path."""
  input_path = pathlib.Path(input_file)
  return str(input_path.with_stem(input_path.stem + "-filtered"))

def main():
  args = _parse_arguments()

  input_file = args.input
  output_file = args.output if args.output is not None else _get_output_file_path(input_file)
  
  from filters import compile_filters, find_time_segments_to_filter
  
  filters = compile_filters(args.filter_word, args.filter_file)
  if len(filters) == 0 and not confirm("No filters configured. Continue anyways?", default=True):
    exit(0)
    
  from transcribe import transcribe, TranscribeOptions
  from audio import filter_audio

  text_segments = transcribe(
    input_file,
    TranscribeOptions(
      model=args.whisper_model,
      device=args.whisper_device,
      compute_type=args.whisper_compute_type,
      condition_on_previous_text='distil' not in args.whisper_model, # Distil models seem prone to repeating themselves
      # hotwords=[decipher(word) if args.encipher_words else word for f in filters for word in [f.pattern[2:-2]]],
      # vad_filter=args.whisper_silence_ms >= 0,
      # vad_parameters=dict(
      #   min_silence_duration_ms=args.whisper_silence_ms
      # ) if args.whisper_silence_ms >= 0 else dict()
    ),
    ignore_cache=args.ignore_cached_transcriptions,
  )

  filter_segments = find_time_segments_to_filter(text_segments, filters, args.encipher_words)
  print(f"Found {len(filter_segments)} audio segments that match filters")
  
  filter_audio(input_file, output_file, filter_segments, args.padding)
  print("Done")

if __name__ == "__main__":
  main()
