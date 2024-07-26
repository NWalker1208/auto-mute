from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment
from tqdm import tqdm
import hashlib, json, os
from strong_typing import serialization

def transcribe(input_file: str, model_name_or_path: str, whisper_kwargs: dict = {}, transcribe_kwargs: dict = {}, ignore_cache: bool = False) -> list[Segment]:
  """Transcribes the given input file using the specified Whisper model and settings."""
  # Check cache
  cache_key = _get_cache_key(input_file, {
    "model_name_or_path": model_name_or_path,
    "whisper_kwargs": whisper_kwargs,
    "transcribe_kwargs": transcribe_kwargs
  })
  if not ignore_cache:
    cached = _get_cached_transcription(cache_key)
    if cached is not None:
      print("Found cached transcription")
      return cached
  
  # Transcribe audio
  model = WhisperModel(model_name_or_path, **whisper_kwargs)
  segments_generator, info = model.transcribe(
    audio=input_file,
    word_timestamps=True,
    **transcribe_kwargs
  )
  
  # https://github.com/SYSTRAN/faster-whisper/issues/80#issuecomment-1502174272
  total_duration = round(info.duration, 2)
  segments = []
  with tqdm(desc="Transcribing audio", total=total_duration, unit=" seconds") as progress:
    for segment in segments_generator:
      progress.update(segment.end - progress.n)
      segments.append(segment)
    progress.update(total_duration - progress.n)

  # Cache result
  _cache_transcription(cache_key, segments)

  return segments

_TRANSCRIPTION_CACHE_DIR = ".transcription_cache"

def _get_file_sha1_digest(path: str) -> str:
  """Computes the SHA-1 hash of the file at the given path."""
  sha1 = hashlib.sha1()
  with open(path, 'rb') as file:
    while True:
      b = file.read(1024)
      if not b:
        break
      sha1.update(b)
  return sha1.hexdigest()

def _get_cache_key(path: str, settings: dict) -> tuple[str, dict]:
  """Computes the cache key for a given path with the given settings. Returns both a hashkey and a dictionary."""
  key_dict = {
    "input_file_sha1": _get_file_sha1_digest(path),
    "settings": settings
  }
  key_hash = hashlib.sha1(json.dumps(key_dict).encode()).hexdigest()
  return key_hash, key_dict

def _get_cached_transcription(key: tuple[str, dict]) -> list[Segment]:
  """Attempts to find a cached transcription for a file with the given SHA-1 digest."""
  key_hash, key_dict = key
  path = os.path.join(_TRANSCRIPTION_CACHE_DIR, f"{key_hash}.json")
  if not os.path.isfile(path):
    return None

  data = None
  with open(path) as file:
    try:
      data = json.load(file)
    except json.JSONDecodeError:
      print("Failed to parse cached transcription")
      return None
  
  if data["key"] != key_dict:
    return None

  try:
    return serialization.json_to_object(list[Segment], data["segments"])
  except:
    print("Failed to parse cached transcription")
    return None

def _cache_transcription(key: tuple[str, dict], segments: list[Segment]):
  """Saves a transcription to the transcription cache."""
  key_hash, key_dict = key
  json_obj = serialization.object_to_json({
    "key": key_dict,
    "segments": segments
  })

  os.makedirs(_TRANSCRIPTION_CACHE_DIR, exist_ok=True)
  path = os.path.join(_TRANSCRIPTION_CACHE_DIR, f"{key_hash}.json")
  with open(path, 'w') as file:
    json.dump(json_obj, file, indent=True)
  print("Added transcription to cache")
