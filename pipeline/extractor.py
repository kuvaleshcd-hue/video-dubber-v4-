"""
extractor.py — Rebuilt for clean audio extraction
Fixes:
  1. Uses ffmpeg directly (more reliable than moviepy for extraction)
  2. Outputs clean 44100Hz mono WAV for Whisper
  3. Removes background noise with a light filter
"""

import subprocess
import tempfile
import os


def extract_audio(video_path: str) -> str:
    """
    Extract audio from video as a clean 44100Hz mono WAV.
    Returns path to the WAV file.
    """
    out_path = tempfile.mktemp(suffix="_extracted.wav")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",                    # no video
        "-acodec", "pcm_s16le",   # uncompressed PCM
        "-ar", "44100",           # 44100 Hz sample rate
        "-ac", "1",               # mono (better for Whisper)
        "-af", "highpass=f=80,lowpass=f=8000",  # light noise filter
        out_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Audio extraction failed:\n{result.stderr[-1000:]}")

    print(f"[extractor] Audio extracted → {out_path}")
    return out_path
