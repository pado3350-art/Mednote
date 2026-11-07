---
name: lecture-transcriber
description: Transcribe lecture audio (MP3/WAV) with faster-whisper and correct medical terminology using the slide vocabulary. Use for the audio stage (not yet implemented in app/).
---

# Lecture Transcriber (planned stage 2)

1. Normalise audio with FFmpeg (16 kHz mono wav).
2. Transcribe with `faster-whisper` (VAD on, language=ko, word timestamps) → `[mm:ss-mm:ss] text` script lines compatible with `app/transcript.py`.
3. Build a glossary from `slides.json` (English terms, drug names, acronyms) and propose corrections; **log original vs corrected** in `transcript_corrections.json`. Never overwrite the raw transcript.
4. Unresolved/low-confidence words → `review_flags`.
