# config.py

DEFAULT_CONFIGS = {
    # Server settings
    "PORT": 5050,
    "HOST": '0.0.0.0',  # Bind address; use 127.0.0.1 for local-only access
    "API_KEY": 'your_api_key_here',  # Fallback API key

    # TTS settings
    "DEFAULT_VOICE": 'en-US-AvaNeural',
    "DEFAULT_RESPONSE_FORMAT": 'mp3',
    "DEFAULT_SPEED": 1.0,
    "DEFAULT_LANGUAGE": 'en-US',

    # Feature flags
    "REQUIRE_API_KEY": True,
    "REMOVE_FILTER": False,
    "EXPAND_API": True,
    "DETAILED_ERROR_LOGGING": True,
    "PCM_TRIM_SILENCE": False,  # Shorten pauses between sentences in streamed PCM
} 