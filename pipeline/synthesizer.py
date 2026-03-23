"""
synthesizer.py — Supports both edge-tts and ElevenLabs voices
Voice format:
  - edge-tts:     "kn-IN-GaganNeural"
  - ElevenLabs:   "elevenlabs:K24eC7JpUgk8zMtQYrpV"
"""

import os
import asyncio
import tempfile
import subprocess
import requests
import edge_tts
from pydub import AudioSegment

TARGET_SAMPLE_RATE = 44100
MIN_SPEED          = 0.75
MAX_SPEED          = 1.80
TARGET_DBFS        = -14.0

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")


# ── helpers ──────────────────────────────────────────────────────────────────

def _ms(seconds: float) -> int:
    return max(0, int(seconds * 1000))


def _normalize(clip: AudioSegment) -> AudioSegment:
    if clip.dBFS == float("-inf"):
        return clip
    return clip.apply_gain(TARGET_DBFS - clip.dBFS)


def _fit_to_window(clip: AudioSegment, window_ms: int) -> AudioSegment:
    clip_len = len(clip)
    if clip_len == 0 or window_ms == 0:
        return AudioSegment.silent(duration=max(window_ms, 1))

    speed = clip_len / window_ms
    speed = max(MIN_SPEED, min(MAX_SPEED, speed))

    if abs(speed - 1.0) >= 0.05:
        new_rate = int(clip.frame_rate * speed)
        clip = clip._spawn(clip.raw_data, overrides={"frame_rate": new_rate})
        clip = clip.set_frame_rate(TARGET_SAMPLE_RATE)

    if len(clip) < window_ms:
        clip = clip + AudioSegment.silent(duration=window_ms - len(clip))
    elif len(clip) > window_ms:
        clip = clip[:window_ms]

    return clip


# ── TTS backends ─────────────────────────────────────────────────────────────

async def _edge_tts_async(text: str, voice: str, out_path: str, retries: int = 3):
    for attempt in range(retries):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(out_path)
            return
        except Exception as e:
            if attempt == retries - 1:
                raise e
            await asyncio.sleep(1.5)


def _synthesize_edge(text: str, voice: str) -> AudioSegment | None:
    tmp = tempfile.mktemp(suffix=".mp3")
    try:
        asyncio.run(_edge_tts_async(text, voice, tmp))
        clip = AudioSegment.from_file(tmp)
        return clip.set_frame_rate(TARGET_SAMPLE_RATE).set_channels(2)
    except Exception as e:
        print(f"[synthesizer] edge-tts error: {e}")
        return None
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def _synthesize_elevenlabs(text: str, voice_id: str) -> AudioSegment | None:
    if not ELEVENLABS_API_KEY:
        print("[synthesizer] ⚠ ELEVENLABS_API_KEY not set in .env!")
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",   # supports Indian languages
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            print(f"[synthesizer] ElevenLabs error {response.status_code}: {response.text[:200]}")
            return None

        tmp = tempfile.mktemp(suffix=".mp3")
        with open(tmp, "wb") as f:
            f.write(response.content)

        clip = AudioSegment.from_file(tmp)
        os.remove(tmp)
        return clip.set_frame_rate(TARGET_SAMPLE_RATE).set_channels(2)

    except Exception as e:
        print(f"[synthesizer] ElevenLabs request error: {e}")
        return None


# ── public API ───────────────────────────────────────────────────────────────

def synthesize_segments(
    segments: list,
    voice_gender: str = "male",
    voice_male: str = "kn-IN-GaganNeural",
    voice_female: str = "kn-IN-SapnaNeural",
) -> list:
    voice = voice_male if voice_gender.lower() == "male" else voice_female

    results = []

    for i, seg in enumerate(segments):
        start_ms = _ms(seg["start"])
        end_ms   = _ms(seg["end"])
        window   = max(end_ms - start_ms, 100)
        text     = (seg.get("text") or "").strip()

        print(f"[synthesizer] {i+1}/{len(segments)} "
              f"({seg['start']:.1f}s–{seg['end']:.1f}s) voice={voice}: {text[:50]}")

        if not text:
            results.append({
                "start": seg["start"],
                "end":   seg["end"],
                "audio": AudioSegment.silent(duration=window),
            })
            continue

        # ── Choose backend based on voice prefix ─────────────────────────
        if voice.startswith("elevenlabs:"):
            voice_id = voice.replace("elevenlabs:", "")
            clip = _synthesize_elevenlabs(text, voice_id)
            # Fallback to edge-tts if ElevenLabs fails
            if clip is None:
                print(f"[synthesizer] Falling back to edge-tts...")
                fallback = "kn-IN-GaganNeural" if voice_gender.lower() == "male" else "kn-IN-SapnaNeural"
                clip = _synthesize_edge(text, fallback)
        else:
            clip = _synthesize_edge(text, voice)

        if clip is None:
            results.append({
                "start": seg["start"],
                "end":   seg["end"],
                "audio": AudioSegment.silent(duration=window),
            })
            continue

        clip = _normalize(clip)
        clip = _fit_to_window(clip, window)

        results.append({
            "start": seg["start"],
            "end":   seg["end"],
            "audio": clip,
        })

    return results
