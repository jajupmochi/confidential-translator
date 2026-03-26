# Confidential Translator 🛡️

[![CI](https://github.com/example/confidential-translator/actions/workflows/ci.yml/badge.svg)](https://github.com/example/confidential-translator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [中文版 / Chinese README](./README_CN.md)

A fully offline, privacy-first document translation system powered by local Large Language Models (LLMs) via Ollama. 

Built with **Python 3.12 (FastAPI)** and **Vue 3 (Vite + TailwindCSS)**, featuring a beautiful glassmorphism interface.

![Dashboard Preview](docs/docs/assets/dashboard.png) *(Placeholder for screenshot)*

## ✨ Features

- **100% Offline & Secure**: Your data never leaves your machine.
- **Local LLMs**: Uses `qwen3:14b-q4_K_M` (or any Ollama model) for human-like translation quality.
- **Comprehensive File Support**: Translates Text, PDFs, Images (OCR), DOCX, MD, XLSX, and CSV.
- **Export Preserved**: Downloads translated files in their original format.
- **Modern UI**: Vue 3 + Tailwind CSS with a stunning glassmorphism design, dark mode, and responsive layout.
- **Analytics & History**: Built-in SQLite database tracks translation history, timing, and token speed.
- **Cross-Platform**: Installers available for Linux (AppImage/Deb), Windows (Exe), and macOS (Dmg).

## 🚀 Quick Start

### Standalone Release (Recommended)
Download the latest executable for your OS from the [Releases page](https://github.com/example/confidential-translator/releases).

1. Double-click the downloaded executable.
2. **That's it!** The app will automatically attempt to start `ollama` in the background and open the user interface in your default web browser (`http://127.0.0.1:8000`).

*(If you don't have Ollama installed, the app will gracefully warn you and provide download options).*

### Running from Source

```bash
# Clone the repository
git clone https://github.com/example/confidential-translator.git
cd confidential-translator

# Setup & Run (requires `uv` and `npm`)
npm install -C frontend
npm run build -C frontend
cp -r frontend/dist/* backend/app/static/

cd backend
uv sync

# Run the app - it will auto-start Ollama and launch your browser!
uv run python -m app.main
```

## 📚 Documentation

Full documentation is available at [our MkDocs site](https://example.github.io/confidential-translator/).

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, SQLite, `uv`
- **Frontend**: Vue 3, Vite, TypeScript, Pinia, Vue Router, TailwindCSS, Lucide Icons
- **Testing**: Pytest, Vitest, Storybook
- **Packaging**: PyInstaller, GitHub Actions

## 📄 License

MIT License. See `LICENSE` for more information.
