# OpenAI-Compatible Edge-TTS API

This project provides a local, OpenAI-compatible text-to-speech (TTS) API using `edge-tts`. It emulates the OpenAI TTS endpoint (`/v1/audio/speech`), enabling users to generate speech from text with various voice options and playback speeds, just like the OpenAI API.

`edge-tts` uses Microsoft Edge's online text-to-speech service, so it is completely free.

## Features

- **OpenAI-Compatible Endpoint**: `/v1/audio/speech` with similar request structure and behavior.
- **Supported Voices**: Maps OpenAI voices (alloy, echo, fable, onyx, nova, shimmer) to `edge-tts` equivalents.
- **Flexible Formats**: Supports multiple audio formats (mp3, opus, aac, flac, wav, pcm).
- **Adjustable Speed**: Option to modify playback speed (0.25x to 4.0x).
- **Optional Direct Edge-TTS Voice Selection**: Use either OpenAI voice mappings or specify any edge-tts voice directly.

## Getting Started

### Prerequisites

- **Docker** (recommended): Docker and Docker Compose for containerized setup.
- **Python** (optional): For local development, install dependencies in `requirements.txt`.
- **ffmpeg**: Required for audio format conversion and playback speed adjustments.

### Installation

1. **Clone the Repository**:
```bash
git clone https://github.com/your-username/openai-edge-tts.git
cd openai-edge-tts
```

2. **Environment Variables**: Create a `.env` file in the root directory with the following variables:
```
API_KEY=your_api_key_here
PORT=5050

DEFAULT_VOICE=en-US-AndrewNeural
DEFAULT_RESPONSE_FORMAT=mp3
DEFAULT_SPEED=1.0

DEFAULT_LANGUAGE=en-US
```

3. **Run with Docker Compose** (recommended):
```bash
docker-compose up --build
```

Alternatively, **run directly with Docker**:
```bash
docker build -t openai-edge-tts .
docker run -p 5050:5050 --env-file .env openai-edge-tts
```

4. **Access the API**: Your server will be accessible at `http://localhost:5050`.

## Running with Python

If you prefer to run this project directly with Python, follow these steps to set up a virtual environment, install dependencies, and start the server.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/openai-edge-tts.git
cd openai-edge-tts
```

### 2. Set Up a Virtual Environment

Create and activate a virtual environment to isolate dependencies:

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

Use `pip` to install the required packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory and set the following variables:

```plaintext
API_KEY=your_api_key_here
PORT=5050

DEFAULT_VOICE=en-US-AndrewNeural
DEFAULT_RESPONSE_FORMAT=mp3
DEFAULT_SPEED=1.0

DEFAULT_LANGUAGE=en-US
```

### 5. Run the Server

Once configured, start the server with:

```bash
python app/server.py
```

The server will start running at `http://localhost:5000`.

### 6. Test the API

You can now interact with the API at `http://localhost:5000/v1/audio/speech` and other available endpoints. See the [Usage](#usage) section for request examples.
    

### Usage

#### Endpoint: `/v1/audio/speech`

Generates audio from the input text. Available parameters:

**Required Parameter:**

- **input** (string): The text to be converted to audio (up to 4096 characters).

**Optional Parameters:**

- **model** (string): Set to "tts-1" or "tts-1-hd" (default: `"tts-1"`).
- **voice** (string): One of the OpenAI-compatible voices (alloy, echo, fable, onyx, nova, shimmer) or any valid `edge-tts` voice (default: `"en-US-AndrewNeural"`).
- **response_format** (string): Audio format. Options: `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm` (default: `mp3`).
- **speed** (number): Playback speed (0.25 to 4.0). Default is `1.0`.

Example request with `curl` and saving the output to an mp3 file:

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d '{
    "input": "Hello, I am your AI assistant! Just let me know how I can help bring your ideas to life.",
    "voice": "echo",
    "response_format": "mp3",
    "speed": 1.0
  }' \
  --output speech.mp3
```

Or, to be in line with the OpenAI API endpoint parameters:

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d '{
    "model": "tts-1",
    "input": "Hello, I am your AI assistant! Just let me know how I can help bring your ideas to life.",
    "voice": "alloy"
  }' \
  --output speech.mp3
```

### Additional Endpoints

- **GET /v1/models**: Lists available TTS models.
- **GET /v1/voices**: Lists all `edge-tts` voices, with language support information.

### Contributing

Contributions are welcome! Please fork the repository and create a pull request for any improvements.

### License

This project is licensed under GNU General Public License v3.0 (GPL-3.0)