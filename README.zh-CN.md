# OpenAI 兼容 Edge-TTS API 🗣️

![GitHub stars](https://img.shields.io/github/stars/travisvn/openai-edge-tts?style=social)
![GitHub forks](https://img.shields.io/github/forks/travisvn/openai-edge-tts?style=social)
![GitHub repo size](https://img.shields.io/github/repo-size/travisvn/openai-edge-tts)
![GitHub top language](https://img.shields.io/github/languages/top/travisvn/openai-edge-tts)
![GitHub last commit](https://img.shields.io/github/last-commit/travisvn/openai-edge-tts?color=red)
[![Discord](https://img.shields.io/badge/Discord-Voice_AI_%26_TTS_Tools-blue?logo=discord&logoColor=white)](https://discord.gg/GkFbBCBqJ6)
[![LinkedIn](https://img.shields.io/badge/Connect_on_LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)](https://linkedin.com/in/travisvannimwegen)

[English](README.md) | [中文](README.zh-CN.md)

本项目提供了一个本地的、兼容 OpenAI 的文本转语音 (TTS) API，使用 `edge-tts` 实现。它模拟了 OpenAI 的 TTS 接口 (`/v1/audio/speech`)，使用户能够以不同的声音选项和播放速度生成语音，就像使用 OpenAI API 一样。

`edge-tts` 使用 Microsoft Edge 的在线文本转语音服务，因此它是完全免费的。

[在 Docker Hub 上查看此项目](https://hub.docker.com/r/travisvn/openai-edge-tts)

# 如果您觉得这个项目有帮助，请给我们一个 ⭐️ 星标

## 特点

- **兼容 OpenAI 的端点**：`/v1/audio/speech` 具有相似的请求结构和行为。
- **SSE 流式传输支持**：当指定 `stream_format: "sse"` 时，通过服务器发送事件进行实时音频流式传输。
- **支持的声音**：将 OpenAI 的声音 (alloy, echo, fable, onyx, nova, shimmer) 映射到 `edge-tts` 的等效声音。
- **灵活的格式**：支持多种音频格式 (mp3, opus, aac, flac, wav, pcm)。
- **可调节的速度**：可以修改播放速度 (0.25x 到 4.0x)。
- **可选的直接 Edge-TTS 声音选择**：可以使用 OpenAI 声音映射或直接指定[任何 edge-tts 声音](https://tts.travisvn.com)。

## ⚡️ 快速开始

最简单的开始方式是运行下面的命令，无需额外配置：

```bash
docker run -d -p 5050:5050 travisvn/openai-edge-tts:latest
```

这将在端口 5050 上运行服务，使用所有默认配置。

_(显然，这需要 Docker)_

## 设置

### 前提条件

- **Docker**（推荐）：用于容器化设置的 Docker 和 Docker Compose。
- **Python**（可选）：对于本地开发，安装 `requirements.txt` 中的依赖项。
- **ffmpeg**（可选）：用于音频格式转换。如果仅使用 mp3，则不需要。

### 安装

1. **克隆仓库**：

```bash
git clone https://github.com/travisvn/openai-edge-tts.git
cd openai-edge-tts
```

2. **环境变量**：在根目录创建一个 `.env` 文件，包含以下变量：

```
API_KEY=your_api_key_here
PORT=5050

DEFAULT_VOICE=en-US-AvaNeural
DEFAULT_RESPONSE_FORMAT=mp3
DEFAULT_SPEED=1.0

DEFAULT_LANGUAGE=en-US

REQUIRE_API_KEY=True
REMOVE_FILTER=False
EXPAND_API=True
DETAILED_ERROR_LOGGING=True
```

或者，复制默认的 `.env.example` 文件：

```bash
cp .env.example .env
```

3. **使用 Docker Compose 运行**（推荐）：

```bash
docker compose up --build
```

使用 `-d` 在"分离模式"下运行 docker compose，这意味着它将在后台运行并释放你的终端。

```bash
docker compose up -d
```

<details>
<summary>

#### 使用 Docker Compose 和 FFmpeg 进行本地构建

</summary>

默认情况下，`docker compose up --build` 创建的是不包含 `ffmpeg` 的最小镜像。如果您正在本地构建（克隆此仓库后）并需要 `ffmpeg` 进行音频格式转换（超出 MP3），您可以在构建中包含它。

这由 `INSTALL_FFMPEG_ARG` 构建参数控制。通过以下方式之一设置此环境变量为 `true`：

1.  **在命令前加前缀：**
    ```bash
    INSTALL_FFMPEG_ARG=true docker compose up --build
    ```
2.  **添加到您的 `.env` 文件中：**
    在项目根目录的 `.env` 文件中添加此行：
    ```env
    INSTALL_FFMPEG_ARG=true
    ```
    然后，运行 `docker compose up --build`。
3.  **导出到您的 shell 环境中：**
    将 `export INSTALL_FFMPEG_ARG=true` 添加到您的 shell 配置中（例如，`~/.zshrc`、`~/.bashrc`）并重新加载 shell。然后 `docker compose up --build` 将使用它。

这适用于本地构建。对于预构建的 Docker Hub 镜像，向版本添加 `latest-ffmpeg` 标签

```bash
docker run -d -p 5050:5050 -e API_KEY=your_api_key_here -e PORT=5050 travisvn/openai-edge-tts:latest-ffmpeg
```

---

</details>

或者，**直接使用 Docker 运行**：

```bash
docker build -t openai-edge-tts .
docker run -p 5050:5050 --env-file .env openai-edge-tts
```

要在后台运行容器，在 `docker run` 命令后添加 `-d`：

```bash
docker run -d -p 5050:5050 --env-file .env openai-edge-tts
```

4. **访问 API**：您的服务器将在 `http://localhost:5050` 可用。

<details>
<summary>

## 使用 Python 运行

</summary>

如果您更喜欢直接使用 Python 运行这个项目，请按照以下步骤设置虚拟环境、安装依赖项并启动服务器。

### 1. 克隆仓库

```bash
git clone https://github.com/travisvn/openai-edge-tts.git
cd openai-edge-tts
```

### 2. 设置虚拟环境

创建并激活一个虚拟环境以隔离依赖项：

```bash
# 对于 macOS/Linux
python3 -m venv venv
source venv/bin/activate

# 对于 Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 安装依赖项

使用 `pip` 安装 `requirements.txt` 中列出的所需包：

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

在根目录中创建一个 `.env` 文件并设置以下变量：

```plaintext
API_KEY=your_api_key_here
PORT=5050

DEFAULT_VOICE=en-US-AvaNeural
DEFAULT_RESPONSE_FORMAT=mp3
DEFAULT_SPEED=1.0

DEFAULT_LANGUAGE=en-US

REQUIRE_API_KEY=True
REMOVE_FILTER=False
EXPAND_API=True
DETAILED_ERROR_LOGGING=True
```

### 5. 运行服务器

配置完成后，启动服务器：

```bash
python app/server.py
```

服务器将在 `http://localhost:5050` 上运行。

### 6. 测试 API

现在您可以在 `http://localhost:5050/v1/audio/speech` 和其他可用端点上与 API 交互了。有关请求示例，请参见[使用方法](#usage)部分。

</details>

<details>
<summary>

## 使用方法

</summary>

#### 端点：`/v1/audio/speech`

根据输入文本生成音频。可用参数：

**必需参数：**

- **input** (string)：要转换为音频的文本（最多 4096 个字符）。

**可选参数：**

- **model** (string)：设置为 "tts-1" 或 "tts-1-hd"（默认：`"tts-1"`）。
- **voice** (string)：OpenAI 兼容的声音之一 (alloy, echo, fable, onyx, nova, shimmer) 或任何有效的 `edge-tts` 声音（默认：`"en-US-AvaNeural"`）。
- **response_format** (string)：音频格式。选项：`mp3`、`opus`、`aac`、`flac`、`wav`、`pcm`（默认：`mp3`）。
- **speed** (number)：播放速度（0.25 到 4.0）。默认为 `1.0`。
- **stream_format** (string)：响应格式。选项：`"audio"`（原始音频数据，默认）或 `"sse"`（带 JSON 事件的服务器发送事件流式传输）。

**注意：** 该 API 完全兼容 OpenAI 的 TTS API 规范。目前不支持 `instructions` 参数（用于微调声音特性），但所有其他参数的工作方式与 OpenAI 的实现相同。

#### 标准音频生成

使用 `curl` 的请求示例，并将输出保存到 mp3 文件：

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d '{
    "input": "你好，我是你的AI助手！请告诉我如何帮助你实现你的想法。",
    "voice": "echo",
    "response_format": "mp3",
    "speed": 1.1
  }' \
  --output speech.mp3
```

#### 直接音频播放（类似 OpenAI）

您可以将音频直接通过管道传输到 `ffplay` 进行即时播放，就像 OpenAI 的 API 一样：

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "今天是构建人们喜爱的东西的美好一天！",
    "voice": "alloy",
    "response_format": "mp3"
  }' | ffplay -i -
```

或者不保存到文件的即时播放：

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "这将立即播放而不保存到磁盘！",
    "voice": "shimmer"
  }' | ffplay -autoexit -nodisp -i -
```

或者，与 OpenAI API 端点参数保持一致：

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d '{
    "model": "tts-1",
    "input": "你好，我是你的AI助手！请告诉我如何帮助你实现你的想法。",
    "voice": "alloy"
  }' \
  --output speech.mp3
```

#### 服务器发送事件 (SSE) 流式传输

对于需要结构化流事件的应用程序（如网页应用），使用 SSE 格式：

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d '{
    "model": "tts-1",
    "input": "这将作为服务器发送事件流式传输，包含包含 base64 编码音频块的 JSON 数据。",
    "voice": "alloy",
    "stream_format": "sse"
  }'
```

**SSE 响应格式：**

```
data: {"type": "speech.audio.delta", "audio": "base64-encoded-audio-chunk"}

data: {"type": "speech.audio.delta", "audio": "base64-encoded-audio-chunk"}

data: {"type": "speech.audio.done", "usage": {"input_tokens": 12, "output_tokens": 0, "total_tokens": 12}}
```

#### JavaScript/网页使用

使用 fetch API 进行 SSE 流式传输的示例：

```javascript
async function streamTTSWithSSE(text) {
  const response = await fetch('http://localhost:5050/v1/audio/speech', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer your_api_key_here',
    },
    body: JSON.stringify({
      input: text,
      voice: 'alloy',
      stream_format: 'sse',
    }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  const audioChunks = [];

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));

        if (data.type === 'speech.audio.delta') {
          // 解码 base64 音频块
          const audioData = atob(data.audio);
          const audioArray = new Uint8Array(audioData.length);
          for (let i = 0; i < audioData.length; i++) {
            audioArray[i] = audioData.charCodeAt(i);
          }
          audioChunks.push(audioArray);
        } else if (data.type === 'speech.audio.done') {
          console.log('语音合成完成:', data.usage);

          // 合并所有块并播放
          const totalLength = audioChunks.reduce(
            (sum, chunk) => sum + chunk.length,
            0
          );
          const combinedArray = new Uint8Array(totalLength);
          let offset = 0;
          for (const chunk of audioChunks) {
            combinedArray.set(chunk, offset);
            offset += chunk.length;
          }

          const audioBlob = new Blob([combinedArray], { type: 'audio/mpeg' });
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          audio.play();
          return;
        }
      }
    }
  }
}

// 使用方法
streamTTSWithSSE('你好，这是SSE流式传输！');
```

#### 国际语言示例

一个英语以外的语言示例：

```bash
curl -X POST http://localhost:5050/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key_here" \
  -d '{
    "model": "tts-1",
    "input": "じゃあ、行く。電車の時間、調べておくよ。",
    "voice": "ja-JP-KeitaNeural"
  }' \
  --output speech.mp3
```

#### 其他端点

- **POST/GET /v1/models**：列出可用的 TTS 模型。
- **POST/GET /v1/voices**：为给定语言/区域设置列出 `edge-tts` 声音。
- **POST/GET /v1/voices/all**：列出所有 `edge-tts` 声音，包含语言支持信息。

</details>

### 贡献

欢迎贡献！请 fork 此仓库并为任何改进创建 pull request。

### 许可证

本项目采用 GNU 通用公共许可证 v3.0 (GPL-3.0) 授权，预期的可接受用途是个人使用。对于企业或非个人使用 `openai-edge-tts`，请联系我：tts@travisvn.com

---

## 示例用例

> [!TIP]
> 如果遇到问题，将 `localhost` 替换为您的本地 IP（例如 `192.168.0.1`）
>
> _可能的情况是，当在不同的服务器/计算机上访问此端点或者当调用来自其他源（如 Open WebUI）时，您需要将 URL 从 `localhost` 更改为您的本地 IP（类似 `192.168.0.1` 或类似的）_

# Open WebUI

打开管理面板，转到设置 -> 音频

下面，您可以看到为使用此项目替代 OpenAI 端点而进行的正确配置的屏幕截图

![Open WebUI 管理设置中为此项目添加正确端点的音频屏幕截图](https://utfs.io/f/MMMHiQ1TQaBo9GgL4WcUbjSRlqi86sV3TXh47KYBJCkdQ20M)

如果您在 Docker 中同时运行 Open WebUI 和此项目，API 端点 URL 可能是 `http://host.docker.internal:5050/v1`

> [!NOTE]
> 查看[Open WebUI 与 OpenAI Edge TTS 集成](https://docs.openwebui.com/tutorials/text-to-speech/openai-edge-tts-integration)的官方文档

# AnythingLLM

在 1.6.8 版本中，AnythingLLM 添加了对"通用 OpenAI TTS 提供者"的支持 — 这意味着我们可以在 AnythingLLM 中使用此项目作为 TTS 提供者

打开设置并转到语音（在 AI 提供者下）

下面，您可以看到为使用此项目替代 OpenAI 端点而进行的正确配置的屏幕截图

![AnythingLLM 语音设置中为此项目添加正确端点的屏幕截图](https://utfs.io/f/MMMHiQ1TQaBoGx6WUTRDJUWPLqoMsXiNkajAdVOwgcxH6uv7)

---

## 快速信息

- `your_api_key_here` 永远不需要替换 — 不需要"真正的" API 密钥。使用您喜欢的任何字符串。
- 最快的启动方式是安装 docker 并运行以下命令：

```bash
docker run -d -p 5050:5050 -e API_KEY=your_api_key_here -e PORT=5050 travisvn/openai-edge-tts:latest
```

---

# 声音样本 🎙️

[播放声音样本并查看所有可用的 Edge TTS 声音](https://tts.travisvn.com/)
