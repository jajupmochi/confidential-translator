# Architecture

## System Overview

```mermaid
graph TB
    subgraph Frontend ["Vue 3 Frontend"]
        A[TranslateView] --> B[FileTranslateView]
        C[HistoryView] --> D[DashboardView]
        E[SettingsView] --> F[ModelsView]
    end

    subgraph Backend ["FastAPI Backend"]
        G[API Routes] --> H[Translation Service]
        G --> I[History Service]
        G --> J[Export Service]
        H --> K[Ollama Service]
        G --> L[Streaming SSE]
    end

    subgraph Data ["Data Layer"]
        M[(SQLite DB)]
        N[File System]
    end

    subgraph LLM ["LLM Engine"]
        O[Ollama Server]
        P[Local Models]
    end

    Frontend -->|REST + SSE| Backend
    I --> M
    J --> N
    K --> O
    O --> P
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3, Vite, TypeScript, Pinia, Vue Router, TailwindCSS v4, Lucide Icons, vue-i18n |
| Backend | Python 3.12, FastAPI, SQLAlchemy (async), Pydantic v2 |
| Database | SQLite via aiosqlite |
| LLM | Ollama (local inference) |
| File Processing | PyMuPDF, Tesseract OCR, python-docx, openpyxl, pandas |
| Packaging | PyInstaller, Docker, GitHub Actions |

## Key Design Decisions

- **SSE streaming** for real-time translation output (not WebSocket — simpler, one-directional)
- **SPA with middleware fallback** — FastAPI serves Vue app with a custom `SPAFallbackMiddleware` for client-side routing
- **Cross-platform native dialogs** — OS-specific file dialogs (kdialog, zenity, osascript, PowerShell) instead of heavy Qt/Electron dependencies
