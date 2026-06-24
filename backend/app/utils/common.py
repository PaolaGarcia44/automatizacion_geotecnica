"""Utilidades compartidas del sistema — Single Source of Truth.

Estas funciones estaban duplicadas en excel_service, word_service y
document_service. Centralizar aquí garantiza comportamiento idéntico en todos
los documentos generados.
"""
from __future__ import annotations

import unicodedata
from datetime import date, datetime
from typing import Optional, Tuple


def normalize(text: str) -> str:
    """Elimina tildes y convierte a minúsculas.

    Fuente única para: búsqueda en COLOR_MAP, comparación de hojas Excel,
    coincidencia de municipios.

    Equivalente a excel_service._normalize y profile_3d_service._norm —
    centralizado aquí para que ambos servicios produzcan el mismo resultado.
    """
    nfkd = unicodedata.normalize("NFD", text or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def split_project_location(value: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Separa 'Proyecto - Ubicación' en (proyecto, ubicacion).

    Fuente única — reemplaza las implementaciones idénticas que existían en
    excel_service._split_project_location y word_service._split_project_location.
    """
    if value is None:
        return None, None
    try:
        text = str(value).strip()
    except Exception:
        return str(value), None

    if not text:
        return None, None

    separators = [" - ", " | ", " / ", " — ", " – ", "\n", "-"]
    for sep in separators:
        if sep in text:
            left, right = text.split(sep, 1)
            left = left.strip(" -|/,\t\r\n")
            right = right.strip(" -|/,\t\r\n")
            if left and right:
                return left, right

    return text, None


def parse_fecha(value) -> Optional[date]:
    """Convierte date, datetime o cadena ISO en un objeto date.

    Fuente única — reemplaza el bloque de parseo inline en document_service
    y el método _parse_fecha de word_service.
    """
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except Exception:
            try:
                return date.fromisoformat(value)
            except Exception:
                return None
    return None
