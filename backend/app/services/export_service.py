"""Export service — convert translated text back to original file formats."""

import csv
import io
import logging

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting translated content to various file formats."""

    async def export(self, translated_text: str, file_type: str, file_name: str) -> tuple[bytes, str, str]:
        """Export translated text to the specified format.

        Returns:
            Tuple of (file bytes, content type, filename with extension).
        """
        exporters = {
            ".txt": self._export_text,
            ".md": self._export_text,
            ".csv": self._export_csv,
            ".xlsx": self._export_xlsx,
        }

        exporter = exporters.get(file_type, self._export_text)
        return await exporter(translated_text, file_name, file_type)

    async def _export_text(
        self, text: str, name: str, ext: str
    ) -> tuple[bytes, str, str]:
        """Export as plain text or markdown."""
        if not ext or ext not in (".txt", ".md"):
            ext = ".txt"
        content_type = "text/markdown" if ext == ".md" else "text/plain"
        return text.encode("utf-8"), content_type, f"{name}{ext}"

    async def _export_csv(
        self, text: str, name: str, ext: str
    ) -> tuple[bytes, str, str]:
        """Export as CSV (assumes pipe-separated table text)."""
        output = io.StringIO()
        writer = csv.writer(output)
        for line in text.strip().split("\n"):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if cells:
                writer.writerow(cells)
        return output.getvalue().encode("utf-8"), "text/csv", f"{name}.csv"

    async def _export_xlsx(
        self, text: str, name: str, ext: str
    ) -> tuple[bytes, str, str]:
        """Export as XLSX spreadsheet."""
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Translation"

        for row_idx, line in enumerate(text.strip().split("\n"), 1):
            if line.startswith("## Sheet:"):
                continue
            cells = [c.strip() for c in line.split("|") if c.strip()]
            for col_idx, cell in enumerate(cells, 1):
                ws.cell(row=row_idx, column=col_idx, value=cell)

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        return buffer.getvalue(), content_type, f"{name}.xlsx"


# Singleton instance
export_service = ExportService()
