# Document Translation

## Supported Formats

| Format | Extension | Method |
|--------|-----------|--------|
| PDF | `.pdf` | PyMuPDF text extraction |
| Images | `.png`, `.jpg`, `.jpeg` | Tesseract OCR |
| Word | `.docx` | python-docx |
| Markdown | `.md` | Direct text |
| Plain text | `.txt` | Direct text |
| Excel | `.xlsx` | openpyxl |
| CSV | `.csv` | pandas |

## Workflow

1. **Drop or browse** — Drag a file onto the drop zone, or click to open your OS file browser
2. **Select languages** — Choose source and target language
3. **Translate** — Click Translate; the content streams in real-time
4. **Download** — Save the translated file via the native OS save dialog

## Native File Dialog

The download button opens your operating system's native save dialog:

- **Linux**: KDE (kdialog) or GNOME (zenity)
- **macOS**: Native Cocoa dialog via osascript
- **Windows**: PowerShell System.Windows.Forms

The filename is pre-filled as `translated_<original_name>`.
