# config.py

DEFAULT_CONFIGS = {
    # Server settings
    "PORT": 5050,
    "API_KEY": 'your_api_key_here',  # Fallback API key

    # TTS settings
    "DEFAULT_VOICE": 'en-US-AvaNeural',
    "DEFAULT_RESPONSE_FORMAT": 'mp3',
    "DEFAULT_SPEED": 1.0,
    "DEFAULT_LANGUAGE": 'en-US',

    # Backend selection — which synthesis engine actually runs.
    # Values: "edge-tts" (default, free Microsoft Edge voices) or "60db".
    # When "60db" is selected, SIXTYDB_API_KEY must also be set.
    "TTS_BACKEND": 'edge-tts',
    "SIXTYDB_API_KEY": '',
    # Default 60db voice when the incoming `voice` field isn't a UUID
    # (e.g. an OpenAI voice name like "alloy" arrives via /v1/audio/speech).
    # The shipped default — "Zara" — is documented at GET /default-voices.
    "SIXTYDB_DEFAULT_VOICE_ID": 'fbb75ed2-975a-40c7-9e06-38e30524a9a1',

    # Feature flags
    "REQUIRE_API_KEY": True,
    "REMOVE_FILTER": False,
    "EXPAND_API": True,
    "DETAILED_ERROR_LOGGING": True,
}