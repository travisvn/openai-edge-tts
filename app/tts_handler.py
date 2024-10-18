# tts_handler.py

import edge_tts
import asyncio
import tempfile
import subprocess
import os

# Language default (environment variable)
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en-US')

# OpenAI voice names mapped to edge-tts equivalents
voice_mapping = {
    'alloy': 'en-US-AvaNeural',
    'echo': 'en-US-AndrewNeural',
    'fable': 'en-GB-SoniaNeural',
    'onyx': 'en-US-EricNeural',
    'nova': 'en-US-SteffanNeural',
    'shimmer': 'en-US-EmmaNeural'
}

async def _generate_audio(text, voice, response_format, speed):
    # Determine if the voice is an OpenAI-compatible voice or a direct edge-tts voice
    edge_tts_voice = voice_mapping.get(voice, voice)  # Use mapping if in OpenAI names, otherwise use as-is

    # Generate the TTS output in mp3 format first
    temp_output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    communicator = edge_tts.Communicate(text, edge_tts_voice)
    await communicator.save(temp_output_file.name)

    # If the requested format is mp3 and speed is 1.0, return the generated file directly
    if response_format == "mp3" and speed == 1.0:
        return temp_output_file.name

    # Convert to the requested format if not mp3 or if speed adjustment is needed
    converted_output_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{response_format}")
    
    # ffmpeg playback speed adjustment
    speed_filter = f"atempo={speed}" if response_format != "pcm" else f"asetrate=44100*{speed},aresample=44100"
    ffmpeg_command = [
        "ffmpeg", "-i", temp_output_file.name, 
        "-filter:a", speed_filter,  # Apply speed adjustment
        "-f", response_format, "-y",
        converted_output_file.name
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error in audio conversion: {e}")

    return converted_output_file.name

def generate_speech(text, voice, response_format, speed=1.0):
    return asyncio.run(_generate_audio(text, voice, response_format, speed))

def get_models():
    return [
        {"id": "tts-1", "name": "Text-to-speech v1"},
        {"id": "tts-1-hd", "name": "Text-to-speech v1 HD"}
    ]

async def _get_voices(language=None):
    # List all voices, filter by language if specified
    all_voices = await edge_tts.list_voices()
    language = language or DEFAULT_LANGUAGE  # Use default if no language specified
    filtered_voices = [
        {"name": v['ShortName'], "gender": v['Gender'], "language": v['Locale']}
        for v in all_voices if language is 'all' or language is None or v['Locale'] == language
    ]
    return filtered_voices

def get_voices(language=None):
    return asyncio.run(_get_voices(language))
