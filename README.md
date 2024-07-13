# auto-mute

A command-line tool to automatically mute specific words from audio and video files. Currently just a proof-of-concept. Originally intended for the censoring of profanity, but I've tried to make it a bit more general purpose.

Uses ffmpeg and OpenAI Whisper (via whisper.cpp).

## Usage

Currently only tested on WSL.

Before running the program, you must run `make` in the whisper.cpp directory.

Right now, the program just uses hard-coded paths for the input and output files. It expects there to be a `video.mp4` file in the working directory, and it will output a `filtered-video.mp4` file. I plan to make this much more flexible in the future.

## To-do

- Improve command line interface:
  - Arguments for input and output files.
  - Arguments for which words/patterns to filter.
  - Arguments for other settings to pass on to whisper.cpp.
  - Show less output from tools.
- Avoid writing intermediate files to disk, or at least keep them in a temp directory.
- Avoid re-extracting/transcribing audio if the input file hasn't changed.
- Get more accurate word-level timestamps.
  - The whisper library's "word timestamps" option seems to work better than the token-level timestamps I get from whisper.cpp. This option uses "the cross-attention pattern and dynamic time warping."
  - In theory, whisper.cpp's built-in dtw option should provide similar output, but I haven't been able to get this feature to work.
  - The following repositories also implement word-level timestamps:
    - [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped)
    - [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
    - [whisperX](https://github.com/m-bain/whisperX)
  - [Forced alignment](https://github.com/pettarin/forced-alignment-tools) may be another option.
