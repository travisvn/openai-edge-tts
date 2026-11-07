"""Run with python -m unittest discover -s tests -v; no network required."""
import base64
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
os.environ['REQUIRE_API_KEY'] = 'True'
os.environ['API_KEY'] = 'unit-test-only-key'
import server
import tts_handler

class StreamingTests(unittest.TestCase):
    def test_sync_wrapper_yields_chunks_before_generator_finishes(self):
        state = []
        async def source(*args):
            yield b'first'
            state.append('resumed')
            yield b'second'
        with patch.object(tts_handler, '_generate_audio_stream', source):
            stream = tts_handler.generate_speech_stream('hello', 'alloy')
            self.assertEqual(next(stream), b'first')
            self.assertEqual(state, [])
            self.assertEqual(list(stream), [b'second'])
        self.assertEqual(state, ['resumed'])

    def test_sse_usage_keeps_original_unicode_characters(self):
        text = '  你好，世界！ **测试**  '
        with patch.object(server, 'generate_speech_stream', return_value=iter([b'one', b'two'])):
            response = server.app.test_client().post('/v1/audio/speech',
                json={'input': text, 'voice': 'alloy', 'stream_format': 'sse'},
                headers={'Authorization': 'Bearer unit-test-only-key'})
            events = [json.loads(line[6:]) for line in response.get_data(as_text=True).splitlines() if line.startswith('data: ')]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(base64.b64decode(events[0]['audio']), b'one')
        self.assertEqual(events[-1]['type'], 'speech.audio.done')
        self.assertEqual(events[-1]['usage']['input_tokens'], len(text))
        self.assertEqual(events[-1]['usage']['total_tokens'], len(text))

    def test_stream_error_is_not_success(self):
        def broken(*args):
            yield b'first'
            raise RuntimeError('deliberate test error')
        with patch.object(server, 'generate_speech_stream', broken):
            events = [json.loads(x[6:]) for x in server.generate_sse_audio_stream('text','alloy',1) if x.startswith('data: ')]
        self.assertEqual(events[-1]['type'], 'error')
        self.assertNotIn('speech.audio.done', [e['type'] for e in events])

    def test_speech_requires_key(self):
        self.assertEqual(server.app.test_client().post('/v1/audio/speech',json={'input':'test','stream_format':'sse'}).status_code,401)
