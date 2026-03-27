# Model Setup

After installing Confidential Translator, you need at least one LLM model for translations.

## Recommended Models

| Model | Size | Best For | Quality |
|-------|------|----------|---------|
| `qwen3:14b-q4_K_M` | ~8 GB | Best balance of quality & speed | ⭐⭐⭐⭐⭐ |
| `qwen3:8b` | ~5 GB | Fast translations, good quality | ⭐⭐⭐⭐ |
| `qwen2.5:7b` | ~4 GB | Lightweight, decent quality | ⭐⭐⭐ |

## Pull a Model

### Via the UI

1. Navigate to the **Models** page in the sidebar
2. Enter the model name (e.g. `qwen3:14b-q4_K_M`) in the pull field
3. Click **Pull** — progress is shown in real-time

### Via CLI

```bash
ollama pull qwen3:14b-q4_K_M
```

## Setting the Default Model

1. Go to **Settings** → **Translation Settings**
2. Set the **Default Model** field to your preferred model name
3. This model will be used automatically for all translations

!!! note "Custom Model Path"
    If you store models on an external drive, update the **Model Storage Path** in Settings → Ollama Engine. Set the `OLLAMA_MODELS` environment variable accordingly.
