"""Word document generation for geotechnical reports."""

import logging
import re
import shutil
import unicodedata
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Tuple

from docx import Document

from app.core.config import settings

logger = logging.getLogger(__name__)

INFORME_TEMPLATE_FILENAME = "INFORME SAN PEDRO 2026-03-26.docx"


class WordService:
    """Generate Word copies from the informe template."""

    def __init__(self):
        self.templates_dir = settings.WORD_TEMPLATES_DIR
        self.generated_dir = settings.GENERATED_DIR

    def get_informe_template_path(self) -> Path:
        return self.templates_dir / INFORME_TEMPLATE_FILENAME

    def _split_project_location(self, value: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        if value is None:
            return None, None
        text = str(value).strip()
        if not text:
            return None, None

        separators = [" - ", " | ", " / ", " — ", " – ", "\n", "-"]
        for separator in separators:
            if separator in text:
                left, right = text.split(separator, 1)
                left = left.strip(" -|/,\t\r\n")
                right = right.strip(" -|/,\t\r\n")
                if left and right:
                    return left, right

        return text, None

    def _parse_fecha(self, fecha_registro) -> Optional[date]:
        if isinstance(fecha_registro, date) and not isinstance(fecha_registro, datetime):
            return fecha_registro
        if isinstance(fecha_registro, datetime):
            return fecha_registro.date()
        if isinstance(fecha_registro, str):
            try:
                return datetime.fromisoformat(fecha_registro).date()
            except Exception:
                try:
                    return date.fromisoformat(fecha_registro)
                except Exception:
                    return None
        return None

    def _format_fecha_for_name(self, fecha_obj: Optional[date], fecha_fallback) -> str:
        if fecha_obj is not None:
            return fecha_obj.isoformat()
        if fecha_fallback is None:
            return ""
        return str(fecha_fallback).strip()

    def build_informe_title(
        self,
        proyecto_ubicacion: str,
        fecha_registro,
    ) -> Tuple[str, str]:
        """Return display title and safe filename (without extension)."""
        _, ubicacion = self._split_project_location(proyecto_ubicacion)
        ubicacion_text = (ubicacion or proyecto_ubicacion or "").strip().upper()
        fecha_obj = self._parse_fecha(fecha_registro)
        fecha_text = self._format_fecha_for_name(fecha_obj, fecha_registro)

        title = " ".join(part for part in ("INFORME", ubicacion_text, fecha_text) if part)
        filename_base = title
        return title, filename_base

    def _sanitize_docx_filename(self, filename_base: str) -> str:
        text = unicodedata.normalize("NFD", filename_base or "").encode("ascii", "ignore").decode("ascii")
        text = re.sub(r'[<>:"/\\|?*]+', "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text or "INFORME"

    def _replace_header_text(self, document: Document, title: str) -> None:
        for section in document.sections:
            header = section.header
            if not header.paragraphs:
                header.add_paragraph(title)
                continue

            first_paragraph = header.paragraphs[0]
            if first_paragraph.runs:
                first_paragraph.runs[0].text = title
                for run in first_paragraph.runs[1:]:
                    run.text = ""
            else:
                first_paragraph.text = title

            for extra_paragraph in header.paragraphs[1:]:
                extra_paragraph.text = ""

    def generate_informe(
        self,
        project_id: str,
        proyecto_ubicacion: str,
        fecha_registro,
    ) -> Tuple[Path, str]:
        """Copy the informe template, set header title, and return path + archive name."""
        template_path = self.get_informe_template_path()
        if not template_path.exists():
            raise FileNotFoundError(f"No se encontró la plantilla Word requerida: {template_path}")

        title, filename_base = self.build_informe_title(proyecto_ubicacion, fecha_registro)
        safe_base = self._sanitize_docx_filename(filename_base)
        output_name = f"{project_id}_{safe_base}.docx"
        output_path = self.generated_dir / output_name
        archive_name = f"{safe_base}.docx"

        shutil.copy2(template_path, output_path)

        document = Document(output_path)
        self._replace_header_text(document, title)
        document.save(output_path)

        logger.info("Informe Word generado: %s", output_path)
        return output_path, archive_name


word_service = WordService()
