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
- Get more accurate timestamps using a [forced alignment tool](https://github.com/pettarin/forced-alignment-tools).
