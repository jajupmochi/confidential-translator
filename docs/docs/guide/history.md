# History & Export

## Translation History

All translations (text and file) are automatically saved to a local SQLite database. The History page provides:

- **Search** — Full-text search across source and translated text
- **Filter** — Filter by type (Text / File / All)
- **Pagination** — Navigate through pages of records
- **Hover tooltips** — See full text content on hover
- **Native file integration** — Click file entries to open their folder location

## Columns

| Column | Description |
|--------|-------------|
| Date | When the translation was performed |
| Type | Text or File translation |
| Languages | Source → Target language pair |
| Source | Original text (click to copy) |
| Translation | Translated text or saved file path (click to copy) |
| Model | Which LLM model was used |
| Speed | Translation performance in tokens/sec |

## Export

After a file translation, clicking **Download** saves the file and updates the Translation column in history with the saved file path.
