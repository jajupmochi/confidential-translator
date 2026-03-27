# Confidential Translator — Implementation Plan

A fully offline, privacy-first document translation system powered by local LLMs (Qwen3/Qwen2.5 via Ollama). Translates text, PDFs, images (OCR), Markdown, XLSX, and CSV across Chinese, English, German, and French — with translation history, statistics dashboard, and export to original format.

## System Specs & Model Strategy

| Resource | Value |
|----------|-------|
| CPU | Intel i7-11700F (16 threads) |
| RAM | 64 GB |
| GPU | NVIDIA RTX 3070 (8 GB VRAM) |
| Python | 3.12 (via `/usr/bin/python3.12`) |
| Node.js | 22.22.1 |
| uv | 0.8.14 |

**Model plan**: Default `qwen3:14b-q4_K_M` (9.3GB, Q4 quantization). With 8GB VRAM, Ollama auto-splits layers between GPU and CPU RAM. Fallbacks: `qwen2.5:7b`, `qwen2.5:3b`. Users can select any model.

---

## Project Structure

```
confidential_translator/
├── backend/                    # Python FastAPI backend
│   ├── pyproject.toml          # uv project config
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app, CORS, static mount
│   │   ├── core/
│   │   │   ├── config.py       # Pydantic Settings
│   │   │   └── database.py     # SQLite for translation history
│   │   ├── api/
│   │   │   ├── translate.py    # POST /api/translate, /api/translate/file
│   │   │   ├── models.py       # GET/POST /api/models
│   │   │   ├── export.py       # POST /api/export
│   │   │   ├── history.py      # GET /api/history, /api/statistics
│   │   │   └── health.py       # GET /api/health
│   │   ├── services/
│   │   │   ├── ollama_service.py
│   │   │   ├── translation_service.py
│   │   │   ├── file_service.py
│   │   │   ├── export_service.py
│   │   │   └── history_service.py
│   │   └── models/
│   │       ├── schemas.py      # Pydantic request/response models
│   │       └── database.py     # SQLAlchemy models
│   └── tests/
│       ├── conftest.py
│       ├── test_translate_api.py
│       ├── test_file_service.py
│       ├── test_translation_service.py
│       ├── test_history_service.py
│       └── test_export_service.py
├── frontend/                   # Vue 3 + Vite + TypeScript
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── .storybook/             # Storybook 8 config
│   │   ├── main.ts
│   │   └── preview.ts
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.ts
│   │   ├── router/index.ts
│   │   ├── stores/             # Pinia stores
│   │   │   ├── translation.ts
│   │   │   ├── settings.ts
│   │   │   └── history.ts
│   │   ├── composables/        # Reusable logic
│   │   │   ├── useTheme.ts
│   │   │   ├── useLocale.ts
│   │   │   └── useOllama.ts
│   │   ├── i18n/               # Vue I18n
│   │   │   ├── index.ts
│   │   │   ├── en.json
│   │   │   ├── zh.json
│   │   │   ├── de.json
│   │   │   └── fr.json
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.vue
│   │   │   │   ├── AppSidebar.vue
│   │   │   │   └── AppHeader.vue
│   │   │   ├── common/
│   │   │   │   ├── GlassCard.vue
│   │   │   │   ├── ThemeToggle.vue
│   │   │   │   ├── LanguageSelector.vue
│   │   │   │   ├── StatusIndicator.vue
│   │   │   │   ├── FileDropZone.vue
│   │   │   │   └── StatCard.vue
│   │   │   └── translation/
│   │   │       ├── TextTranslator.vue
│   │   │       ├── FileTranslator.vue
│   │   │       ├── ModelSelector.vue
│   │   │       ├── TranslationReport.vue
│   │   │       └── LanguagePairSelector.vue
│   │   ├── views/
│   │   │   ├── TranslateView.vue
│   │   │   ├── FileTranslateView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── HistoryView.vue
│   │   │   ├── ModelsView.vue
│   │   │   └── SettingsView.vue
│   │   ├── styles/
│   │   │   ├── variables.css
│   │   │   ├── base.css
│   │   │   ├── themes.css
│   │   │   └── glassmorphism.css
│   │   └── __tests__/
│   │       ├── components/
│   │       └── stores/
│   └── stories/                # Storybook stories
│       ├── GlassCard.stories.ts
│       ├── ThemeToggle.stories.ts
│       ├── TranslationReport.stories.ts
│       └── ...
├── docs/                       # MkDocs Material
│   ├── mkdocs.yml
│   ├── docs/
│   │   ├── index.md            # Product-style homepage
│   │   ├── en/ + zh/           # Bilingual docs
│   │   └── assets/
│   ├── overrides/home.html     # Custom landing page
│   └── stylesheets/extra.css
├── .github/workflows/
│   ├── ci.yml                  # Lint + Test + Build
│   ├── release.yml             # Cross-platform packaging
│   └── docs.yml                # MkDocs → GitHub Pages
├── scripts/
│   ├── setup.sh                # Dev environment setup
│   └── build_packages.py       # Cross-platform packaging script
├── README.md                   # English
├── README_CN.md                # Chinese
├── LICENSE                     # MIT
├── Makefile
└── .gitignore
```

---

## UI/UX Design Specification

### Design System

| Token | Light Mode | Dark Mode |
|-------|-----------|-----------|
| `--bg-primary` | `#F8FAFC` | `#0F172A` |
| `--bg-surface` | `rgba(255,255,255,0.72)` | `rgba(30,41,59,0.72)` |
| `--bg-glass` | `rgba(255,255,255,0.48)` | `rgba(15,23,42,0.48)` |
| `--text-primary` | `#1E293B` | `#F1F5F9` |
| `--text-secondary` | `#64748B` | `#94A3B8` |
| `--accent-primary` | `#6366F1` (Indigo) | `#818CF8` |
| `--accent-success` | `#10B981` | `#34D399` |
| `--accent-warning` | `#F59E0B` | `#FBBF24` |
| `--accent-danger` | `#EF4444` | `#F87171` |
| `--border` | `rgba(0,0,0,0.06)` | `rgba(255,255,255,0.06)` |
| `--shadow` | `0 4px 24px rgba(0,0,0,0.06)` | `0 4px 24px rgba(0,0,0,0.3)` |
| `--radius-sm` | `8px` | `8px` |
| `--radius-md` | `12px` | `12px` |
| `--radius-lg` | `16px` | `16px` |
| `--radius-xl` | `24px` | `24px` |

### Typography
- **Primary**: `Inter` (Google Fonts, headings + body)
- **Monospace**: `JetBrains Mono` (code, stats)
- **Scale**: 14px base, 1.5 line-height, modular scale (1.25)

### Glassmorphism Effects
```css
.glass-card {
  background: var(--bg-glass);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow);
  transition: all 0.2s ease;
}
.glass-card:hover {
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.12);
  transform: translateY(-1px);
}
```

### Layout
- **Sidebar**: 260px width, collapsible, glass effect, nav icons from Lucide
- **Header**: 64px height, glass overlay, contains: breadcrumb, theme toggle, language selector, Ollama status
- **Content**: Fluid, max-width 1400px, 24px padding
- **Responsive**: 375px → 768px → 1024px → 1440px breakpoints

### Pages

1. **Dashboard** (`/`) — Statistics overview
   - Welcome card with Ollama connection status
   - Stat cards: total translations, characters translated, avg time, most used language pair
   - Recent translations list (last 10)
   - Chart: translations per day (bar chart, last 30 days)
   - Chart: language pair distribution (donut chart)

2. **Text Translation** (`/translate`) — Core feature
   - Split pane layout (source left, target right)
   - Source: textarea with char count, language auto-detect badge
   - Target: readonly textarea with copy button, language selector dropdown
   - Model selector in toolbar
   - Translation report card below: time taken, chars in/out, model used, tokens/sec
   - "Translate" button with loading spinner animation

3. **File Translation** (`/translate/file`) — File processing
   - Large drag-and-drop zone (dashed border, icon, file type hints)
   - Supported formats: PDF, PNG/JPG (OCR), MD, XLSX, CSV, DOCX, TXT
   - File preview panel (shows extracted text)
   - Translation progress bar
   - Download translated file button (exports to matching format)
   - Translation report card

4. **History** (`/history`) — Translation logs
   - Searchable, filterable table
   - Columns: date, source lang, target lang, type (text/file), chars, time, model
   - Click to expand: full source and translated text
   - Bulk delete, export history as CSV

5. **Models** (`/models`) — Model management
   - List of installed models with size, params, quant info
   - Recommended model card (based on system specs)
   - Pull new model with progress bar
   - Delete model button

6. **Settings** (`/settings`) — Configuration
   - Default model, default language pair
   - UI language (auto-detect / manual)
   - Theme (light / dark / system)
   - Ollama server URL
   - Translation quality hints (formal / informal / technical)

### Icons
All icons from **Lucide** (SVG, tree-shakeable): `Languages`, `FileText`, `Upload`, `History`, `Settings`, `Sun`, `Moon`, `ChevronDown`, `Copy`, `Download`, `Trash2`, `BarChart3`, `Globe`

### Animations
- Page transitions: fade + slide (150ms)
- Card hover: translateY(-1px) + shadow expand (200ms)
- Button click: scale(0.97) (100ms)
- Loading: pulse animation on translate button
- Sidebar collapse: width transition (200ms)
- Theme switch: smooth color transition on `*` (300ms)

---

## Backend API Design (Swagger)

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | System health + Ollama status |
| `POST` | `/api/translate` | Translate text |
| `POST` | `/api/translate/file` | Upload file, extract, translate |
| `GET` | `/api/models` | List installed Ollama models |
| `POST` | `/api/models/pull` | Pull a model by name |
| `DELETE` | `/api/models/{name}` | Delete a model |
| `GET` | `/api/models/recommend` | Get recommended model for system |
| `POST` | `/api/export` | Export translation to file format |
| `GET` | `/api/history` | List translation history (paginated) |
| `GET` | `/api/history/{id}` | Get single translation detail |
| `DELETE` | `/api/history/{id}` | Delete history entry |
| `GET` | `/api/statistics` | Dashboard statistics |
| `GET` | `/api/detect-language` | Detect text language |

### Translation Response includes Report
```json
{
  "translated_text": "...",
  "report": {
    "source_language": "en",
    "target_language": "zh",
    "model_used": "qwen3:14b-q4_K_M",
    "characters_input": 1024,
    "characters_output": 876,
    "tokens_input": 512,
    "tokens_output": 438,
    "time_taken_ms": 3200,
    "tokens_per_second": 136.9
  }
}
```

### Translation History Record (SQLite)
```sql
CREATE TABLE translation_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  source_language VARCHAR(10),
  target_language VARCHAR(10),
  translation_type VARCHAR(20),  -- 'text' or 'file'
  file_name VARCHAR(255),
  file_type VARCHAR(20),
  source_text TEXT,
  translated_text TEXT,
  model_used VARCHAR(100),
  characters_input INTEGER,
  characters_output INTEGER,
  tokens_input INTEGER,
  tokens_output INTEGER,
  time_taken_ms INTEGER,
  tokens_per_second REAL
);
```

---

## Packaging Strategy

| Platform | Format | Tool |
|----------|--------|------|
| Linux | AppImage + .deb | PyInstaller → appimagetool / fpm |
| Windows | .exe installer | PyInstaller → NSIS |
| macOS | .dmg | PyInstaller → create-dmg |

All packages include bundled Vue frontend as static files served by FastAPI. Ollama must be installed separately (app shows setup wizard).

---

## CI/CD Workflows

### ci.yml (on push/PR to main)
1. **Backend Lint**: `ruff check`, `ruff format --check`
2. **Backend Test**: `pytest --cov`
3. **Frontend Lint**: `eslint`, `prettier --check`
4. **Frontend Test**: `vitest run`
5. **Frontend Build**: `vite build`

### release.yml (on tag v*)
- Matrix: `ubuntu-latest`, `windows-latest`, `macos-latest`
- Build installers, upload to GitHub Release

### docs.yml (on push to main)
- Build MkDocs, deploy to GitHub Pages

---

## Documentation (MkDocs Material)

- **Theme**: `mkdocs-material` with custom homepage override
- **Homepage**: Product-style landing page with hero section, feature cards, screenshots, CTA
- **i18n**: `mkdocs-static-i18n` plugin for EN/CN
- **Sections**: Getting Started, User Guide, File Formats, Configuration, Development Guide, API Reference
- **Demo**: Screenshots of each page, example translation workflows

---

## Verification Plan

### Automated
```bash
# Backend
cd backend && uv run pytest tests/ -v --cov=app
# Frontend
cd frontend && npx vitest run
# Linting
cd backend && uv run ruff check app/ tests/
cd frontend && npx eslint src/ && npx prettier --check src/
# Build
cd frontend && npm run build
```

### CI
Push to GitHub, verify all Actions jobs pass green.
