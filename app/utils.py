# utils.py

from flask import request, jsonify
from functools import wraps
import os
from dotenv import load_dotenv

from config import DEFAULT_CONFIGS

load_dotenv()

def getenv_bool(name: str, default: bool = False) -> bool:
    # The default parameter for getenv_bool is used if the config default itself needs a fallback,
    # or if the call site specifically wants to override the global default.
    # For typical usage, the config default (passed at call site) is preferred.
    return os.getenv(name, str(default)).lower() in ("yes", "y", "true", "1", "t")

API_KEY = os.getenv('API_KEY', DEFAULT_CONFIGS["API_KEY"])
REQUIRE_API_KEY = getenv_bool('REQUIRE_API_KEY', DEFAULT_CONFIGS["REQUIRE_API_KEY"])
DETAILED_ERROR_LOGGING = getenv_bool('DETAILED_ERROR_LOGGING', DEFAULT_CONFIGS["DETAILED_ERROR_LOGGING"])

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not REQUIRE_API_KEY:
            return f(*args, **kwargs)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid API key"}), 401
        token = auth_header.split('Bearer ')[1]
        if token != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Mapping of audio format to MIME type
AUDIO_FORMAT_MIME_TYPES = {
    "mp3": "audio/mpeg",
    "opus": "audio/ogg",
    "aac": "audio/aac",
    "flac": "audio/flac",
    "wav": "audio/wav",
    "pcm": "audio/L16"
}
