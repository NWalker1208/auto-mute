# auto-mute

A command-line tool to automatically mute specific words from audio and video files. Currently just a proof-of-concept. Originally intended for censoring profanity, but I've tried to make it a bit more general purpose.

Uses OpenAI Whisper to transcribe audio and ffmpeg to extract audio and apply filters.


## Usage

> :warning: Currently only tested in WSL.

Install the requirements listed in `requirements.txt`, then run `python src/main.py --help` for usage information.


## To-Do

- Add YouTube support using [pytubefix](https://github.com/JuanBindez/pytubefix).
- Make this work in a browser?


## To-Done

- Improve command line interface:
  - Arguments for input and output files.
  - Arguments for which words/patterns to filter.
  - Show less output from tools.
  - Argument for file of filters to use.
  - Argument for padding to add around words.
  - Arguments for other settings to pass on to whisper (e.g., model).
- Get more accurate word-level timestamps.
  - The whisper library's "word timestamps" option seems to work better than the token-level timestamps I get from whisper.cpp. This option uses "the cross-attention pattern and dynamic time warping."
  - In theory, whisper.cpp's built-in dtw option should provide similar output, but I haven't been able to get this feature to work. See ggerganov/whisper.cpp#2301.
  - I looked at the following repositories which also implement word-level timestamps:
    - [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped)
    - [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
    - [whisperX](https://github.com/m-bain/whisperX)
  - Using a separate [forced alignment tool](https://github.com/pettarin/forced-alignment-tools) was another option.
  - I ended up going with faster-whisper as they implement the DTW approach while being very performant overall.
- Avoid writing intermediate files to disk, or at least keep them in a temp directory.
- Avoid re-extracting/transcribing audio if the input file hasn't changed.
