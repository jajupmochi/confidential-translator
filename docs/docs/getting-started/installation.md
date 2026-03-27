# Installation

## Prerequisites

- **Ollama** — Local LLM runtime ([ollama.com](https://ollama.com))
- **Python 3.12+** — For the backend (if running from source)
- **Node.js 22+** — For the frontend (if running from source)

## Option 1: Docker (Recommended) :material-docker:

The easiest way to run Confidential Translator — no coding knowledge required.

```bash
# Clone the repository
git clone https://github.com/jajupmochi/confidential-translator.git
cd confidential-translator

# Start with Docker Compose (includes Ollama)
docker compose up -d
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

!!! tip "GPU Acceleration"
    For NVIDIA GPU support, uncomment the `deploy` section in `docker-compose.yml` to enable GPU passthrough to Ollama.

## Option 2: Standalone Binary

Download the latest release for your OS from the [Releases page](https://github.com/jajupmochi/confidential-translator/releases).

| Platform | Download |
|----------|----------|
| :fontawesome-brands-linux: Linux | `confidential-translator-linux-amd64` |
| :fontawesome-brands-windows: Windows | `confidential-translator-windows-amd64.exe` |
| :fontawesome-brands-apple: macOS | `confidential-translator-macos-x64` |

1. Download and run the executable
2. The app will auto-start Ollama and open your browser to `http://127.0.0.1:8000`

## Option 3: From Source

```bash
# Clone
git clone https://github.com/jajupmochi/confidential-translator.git
cd confidential-translator

# Build frontend
npm install -C frontend
npm run build -C frontend
cp -r frontend/dist/* backend/app/static/

# Install & run backend
cd backend
uv sync
uv run python -m app.main
```
