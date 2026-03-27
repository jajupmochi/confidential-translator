# API Reference

## Base URL

```
http://127.0.0.1:8000/api
```

## Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | System health check (Ollama status, model availability) |

### Translation

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/translate/stream` | Stream text translation via SSE |
| `POST` | `/api/translate/stream/file` | Stream file translation (multipart upload) |
| `POST` | `/api/translate/stream/file/native` | Stream file translation from native file path |

### History

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/history` | List translation history (paginated) |
| `DELETE` | `/api/history/{id}` | Delete a history record |
| `GET` | `/api/history/statistics` | Get dashboard statistics |

### Models

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/models` | List installed Ollama models |
| `POST` | `/api/models/pull` | Pull (download) a new model |
| `DELETE` | `/api/models/{name}` | Delete an installed model |

### Export

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/export` | Export translated text as a file (browser download) |
| `POST` | `/api/export/native` | Export to native filesystem path |

### Settings

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/settings` | Get current settings |
| `PUT` | `/api/settings` | Update settings |

### Glossary

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/glossaries` | List all glossaries |
| `POST` | `/api/glossaries` | Create a glossary |
| `DELETE` | `/api/glossaries/{id}` | Delete a glossary |
| `GET` | `/api/glossaries/{id}/entries` | List glossary entries |
| `POST` | `/api/glossaries/{id}/entries` | Add an entry |
| `DELETE` | `/api/glossaries/{id}/entries/{entry_id}` | Delete an entry |

### OS Integration

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/system/pick-file` | Open native file picker |
| `GET` | `/api/system/save-file` | Open native save dialog |
| `POST` | `/api/system/open-file` | Open file with default app |
| `POST` | `/api/system/open-folder` | Open parent folder |
