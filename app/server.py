# server.py

from flask import Flask, request, send_file, jsonify
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
import os
import re

from tts_handler import generate_speech, get_models, get_voices
from utils import require_api_key, AUDIO_FORMAT_MIME_TYPES

app = Flask(__name__)
load_dotenv()

API_KEY = os.getenv('API_KEY', 'your_api_key_here')
PORT = int(os.getenv('PORT', 5050))

DEFAULT_VOICE = os.getenv('DEFAULT_VOICE', 'en-US-AndrewNeural')
DEFAULT_RESPONSE_FORMAT = os.getenv('DEFAULT_RESPONSE_FORMAT', 'mp3')
DEFAULT_SPEED = float(os.getenv('DEFAULT_SPEED', 1.2))

# DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'tts-1')

@app.route('/v1/audio/speech', methods=['POST'])
@require_api_key
def text_to_speech():
    data = request.json
    if not data or 'input' not in data:
        return jsonify({"error": "Missing 'input' in request body"}), 400

    text = data.get('input')
    
    # 前置处理
    # 将Markdown格式中表示标题的#号去掉
    text = re.sub(r'^#+\s', '', text, flags=re.MULTILINE)
    # 将Markdown格式中表示列表的*号去掉
    text = re.sub(r'(?:^\s*\*\s|^>\s+\*\s)', '', text, flags=re.MULTILINE)
    # 把长度超过2个的连续下划线去掉（连续下划线通常为选择题填空部份）
    text = re.sub(r'_{2,}', '__', text, flags=re.MULTILINE)
    
    # model = data.get('model', DEFAULT_MODEL)
    voice = data.get('voice', DEFAULT_VOICE)

    response_format = data.get('response_format', DEFAULT_RESPONSE_FORMAT)
    speed = float(data.get('speed', DEFAULT_SPEED))
    
    mime_type = AUDIO_FORMAT_MIME_TYPES.get(response_format, "audio/mpeg")

    # Generate the audio file in the specified format with speed adjustment
    output_file_path = generate_speech(text, voice, response_format, speed)

    # Return the file with the correct MIME type
    return send_file(output_file_path, mimetype=mime_type, as_attachment=True, download_name=f"speech.{response_format}")

@app.route('/v1/models', methods=['GET', 'POST'])
@require_api_key
def list_models():
    return jsonify({"data": get_models()})

@app.route('/v1/voices', methods=['GET', 'POST'])
@require_api_key
def list_voices():
    specific_language = None

    data = request.args if request.method == 'GET' else request.json
    if data and ('language' in data or 'locale' in data):
        specific_language = data.get('language') if 'language' in data else data.get('locale')

    return jsonify({"voices": get_voices(specific_language)})

@app.route('/v1/voices/all', methods=['GET', 'POST'])
@require_api_key
def list_all_voices():
    return jsonify({"voices": get_voices('all')})

print(f" Edge TTS (Free Azure TTS) Replacement for OpenAI's TTS API")
print(f" ")
print(f" * Serving OpenAI Edge TTS")
print(f" * Server running on http://localhost:{PORT}")
print(f" * TTS Endpoint: http://localhost:{PORT}/v1/audio/speech")
print(f" ")

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', PORT), app)
    http_server.serve_forever()
