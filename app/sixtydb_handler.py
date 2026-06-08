# sixtydb_handler.py
"""60db.ai TTS backend.

Mirrors the public surface of tts_handler.py so the dispatch in
tts_handler.generate_speech() / generate_speech_stream() / get_voices()
can switch backends without server.py needing to know about it.

Wire-level docs:
  - https://docs.60db.ai/api-reference/tts/text-to-speech
  - https://docs.60db.ai/api-reference/voices/get-my-voices
  - https://docs.60db.ai/api-reference/voices/get-voices

Only the synchronous /tts-synthesize endpoint is used here. NDJSON stream
and the realtime WebSocket are intentionally out of scope — this server's
SSE streaming path slices a fully-synthesized buffer into events instead.
"""

import base64
import os
import re
import subprocess
import tempfile
from pathlib import Path

import requests

from config import DEFAULT_CONFIGS

# Endpoints
_SYNTHESIZE_URL    = "https://api.60db.ai/tts-synthesize"
_MY_VOICES_URL     = "https://api.60db.ai/myvoices"
_DEFAULT_VOICES_URL = "https://api.60db.ai/default-voices"

# Formats accepted by 60db directly. Anything else → request mp3 from 60db
# and let _maybe_transcode() pick it up via ffmpeg (same trick tts_handler uses).
_NATIVE_FORMATS = {"mp3", "wav", "ogg", "flac"}

# Output format dispatch tables for the ffmpeg transcode path. Mirrors the
# tables in tts_handler._generate_audio so behaviour is identical across
# backends.
_FFMPEG_CODECS = {
    "aac":  "aac",
    "mp3":  "libmp3lame",
    "wav":  "pcm_s16le",
    "opus": "libopus",
    "flac": "flac",
}
_FFMPEG_CONTAINERS = {
    "aac":  "mp4",
    "mp3":  "mp3",
    "wav":  "wav",
    "opus": "ogg",
    "flac": "flac",
}

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)


def _api_key() -> str:
    key = os.getenv("SIXTYDB_API_KEY", DEFAULT_CONFIGS.get("SIXTYDB_API_KEY", ""))
    if not key:
        raise RuntimeError(
            "TTS_BACKEND=60db but SIXTYDB_API_KEY is not set. "
            "Set it in .env or via environment."
        )
    return key


def _resolve_voice_id(voice: str) -> str:
    """OpenAI voice names ('alloy', 'echo', …) and Edge voice strings
    ('en-US-AvaNeural') have no equivalent in 60db's UUID-based voice
    catalog. Anything that doesn't look like a UUID falls back to the
    configured default voice. UUIDs pass through unchanged.
    """
    if voice and _UUID_RE.match(voice):
        return voice
    return os.getenv(
        "SIXTYDB_DEFAULT_VOICE_ID",
        DEFAULT_CONFIGS["SIXTYDB_DEFAULT_VOICE_ID"],
    )


def _clamp_speed(speed: float) -> float:
    """60db /tts-synthesize accepts speed in [0.5, 2.0]; clamp politely."""
    try:
        s = float(speed)
    except (TypeError, ValueError):
        return 1.0
    return max(0.5, min(2.0, s))


def _is_ffmpeg_installed() -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _call_synthesize(text: str, voice_id: str, speed: float, output_format: str) -> bytes:
    """POST /tts-synthesize and return raw audio bytes (base64-decoded)."""
    payload = {
        "text": text,
        "voice_id": voice_id,
        "enhance": True,
        "speed": speed,
        "stability": 50,
        "similarity": 75,
        "output_format": output_format,
    }
    r = requests.post(
        _SYNTHESIZE_URL,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json=payload,
        timeout=120,
    )
    if r.status_code != 200:
        raise RuntimeError(f"60db {r.status_code}: {r.text[:200]}")
    body = r.json()
    if not body.get("success", True) or not body.get("audio_base64"):
        raise RuntimeError(f"60db returned no audio: {body.get('message', 'unknown')}")
    return base64.b64decode(body["audio_base64"])


def _maybe_transcode(src_path: str, src_format: str, dst_format: str) -> str:
    """If 60db gave us src_format but client wants dst_format, ffmpeg it.
    Returns a path to the file in the requested format (which may be src_path
    if no conversion was needed or ffmpeg is unavailable).
    """
    if dst_format == src_format:
        return src_path
    if not _is_ffmpeg_installed():
        # Same degradation as tts_handler.py: log + return original.
        print("FFmpeg is not available. Returning unmodified audio.")
        return src_path

    dst_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{dst_format}")
    dst_path = dst_file.name
    dst_file.close()

    cmd = ["ffmpeg", "-i", src_path, "-c:a", _FFMPEG_CODECS.get(dst_format, "aac")]
    if dst_format != "wav":
        cmd.extend(["-b:a", "192k"])
    cmd.extend(["-f", _FFMPEG_CONTAINERS.get(dst_format, dst_format), "-y", dst_path])

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        Path(dst_path).unlink(missing_ok=True)
        Path(src_path).unlink(missing_ok=True)
        raise RuntimeError(f"FFmpeg error during audio conversion: {exc}") from exc

    Path(src_path).unlink(missing_ok=True)
    return dst_path


# ─────────────────────────────────────────────────────
# Public surface (mirrors tts_handler.py)
# ─────────────────────────────────────────────────────

def generate_speech(text: str, voice: str, response_format: str, speed: float = 1.0) -> str:
    """Buffered synthesis. Returns a path to a temp file in `response_format`."""
    voice_id = _resolve_voice_id(voice)
    speed_v = _clamp_speed(speed)
    fmt_native = response_format if response_format in _NATIVE_FORMATS else "mp3"

    audio_bytes = _call_synthesize(text, voice_id, speed_v, fmt_native)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{fmt_native}")
    tmp.write(audio_bytes)
    tmp.close()
    return _maybe_transcode(tmp.name, fmt_native, response_format)


def generate_speech_stream(text: str, voice: str, speed: float = 1.0):
    """SSE-friendly generator.

    60db's /tts-synthesize is buffered, not streaming, so we synthesise the
    whole MP3 and slice it into ~16 KB chunks — same observable shape as
    edge-tts (Iterator[bytes]) so the SSE handler in server.py works
    unchanged.
    """
    voice_id = _resolve_voice_id(voice)
    speed_v = _clamp_speed(speed)
    audio_bytes = _call_synthesize(text, voice_id, speed_v, "mp3")
    chunk_size = 16 * 1024
    for i in range(0, len(audio_bytes), chunk_size):
        yield audio_bytes[i : i + chunk_size]


def _get_voices_via(url: str) -> list[dict]:
    r = requests.get(
        url,
        headers={"Authorization": f"Bearer {_api_key()}"},
        timeout=30,
    )
    if r.status_code != 200:
        return []
    return (r.json() or {}).get("data") or []


def get_voices(language=None) -> list[dict]:
    """Return Edge-TTS-shaped voice records sourced from 60db.

    Output format mirrors tts_handler.get_voices() so any client probing
    /v1/voices keeps getting {name, gender, language} regardless of backend.
    """
    voices = _get_voices_via(_DEFAULT_VOICES_URL) + _get_voices_via(_MY_VOICES_URL)
    out = []
    for v in voices:
        labels = v.get("labels") or {}
        locale = labels.get("language") or ""
        if language and language != "all" and locale != language:
            continue
        out.append({
            "name": v.get("voice_id", ""),
            "gender": labels.get("gender", ""),
            "language": locale,
        })
    return out


def get_voices_formatted() -> list[dict]:
    """Used by /v1/audio/voices. Returns {id, name} pairs."""
    voices = _get_voices_via(_DEFAULT_VOICES_URL) + _get_voices_via(_MY_VOICES_URL)
    return [{"id": v.get("voice_id", ""), "name": v.get("name", "")} for v in voices]
