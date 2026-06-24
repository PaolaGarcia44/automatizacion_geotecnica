"""Constantes globales del sistema — Single Source of Truth.

Todos los servicios deben importar sus constantes desde este módulo.
Nunca definir colores, secuencias SPT ni rangos de pisos en otro lugar.
"""
from __future__ import annotations

from typing import Dict, List

# ── Mapa de colores ───────────────────────────────────────────────────────────
# Claves pre-normalizadas: sin tildes, minúsculas, espacios internos preservados.
# Tanto excel_service (openpyxl) como profile_3d_service (SVG) importan este mapa.
# Búsqueda: normalizar el nombre de color de entrada → dict.get(key, default).
COLOR_MAP: Dict[str, str] = {
    "beige":           "F5F0D7",
    "beis":            "F5F0D7",
    "cafe":            "8B5A2B",
    "cafe oscuro":     "5C3D2E",
    "cafe claro":      "A0826D",
    "cafe rojizo":     "9B6B4A",
    "marron":          "8B4513",
    "marron claro":    "A0826D",
    "marron oscuro":   "5C3D2E",
    "marron rojizo":   "9B6B4A",
    "amarillo":        "FFD966",
    "amarillo claro":  "FFEB3B",
    "amarillo oscuro": "D4A520",
    "amarillo cafe":   "9B8C00",
    "rojizo":          "C0504D",
    "rojo":            "FF0000",
    "rojo oscuro":     "8B0000",
    "blanco":          "FFFFFF",
    "blanco sucio":    "E8E8E8",
    "gris":            "808080",
    "gris claro":      "D9D9D9",
    "gris oscuro":     "505050",
    "gris azuloso":    "708090",
    "gris amarillento":"A9A9A9",
    "naranja":         "F4B183",
    "naranja claro":   "FFD700",
    "naranja oscuro":  "FF8C00",
    "verde":           "92D050",
    "verde claro":     "C6E0B4",
    "verde oscuro":    "008000",
    "negro":           "000000",
    "negro verdoso":   "1B4D3E",
    "rosa":            "FFC0CB",
    "purpura":         "800080",
    "violeta":         "EE82EE",
    "azul":            "0000FF",
    "azul claro":      "ADD8E6",
    "azul oscuro":     "00008B",
    "turquesa":        "40E0D0",
    "cian":            "00FFFF",
    "crema":           "FFFDD0",
    "mostaza":         "FFDB58",
    "ocre":            "CC7000",
    "siena":           "A0522D",
    "tostado":         "D2B48C",
    "leonado":         "DAA520",
    "grisaceo":        "A9A9A9",
    "pardusco":        "8B7355",
    "oscuro":          "505050",
    "claro":           "E8E8E8",
}


# ── Configuración por rango de pisos ──────────────────────────────────────────
# Fuente única de verdad para todas las decisiones que dependen del número
# de pisos (selección de plantilla, profundidades, conteo SPT, etc.).

def get_pisos_config(pisos: int) -> Dict:
    """Devuelve la configuración correspondiente al rango de pisos indicado.

    Todos los servicios deben llamar esta función en lugar de repetir las
    condiciones if/elif pisos <= 3 / pisos <= 10 / else.
    """
    if pisos <= 3:
        return {
            "template_id":  "1",
            "spt_count":    7,
            "max_depth":    6,
            "expand_levels": 7,
            "f_end_row":    16,
            "perfil_name":  "PERFIL DEL SUELO 6M.xlsx",
        }
    elif pisos <= 10:
        return {
            "template_id":  "2",
            "spt_count":    16,
            "max_depth":    15,
            "expand_levels": 16,
            "f_end_row":    25,
            "perfil_name":  "PERFIL DEL SUELO 15M.xlsx",
        }
    else:
        return {
            "template_id":  "3",
            "spt_count":    25,
            "max_depth":    25,
            "expand_levels": 26,
            "f_end_row":    35,
            "perfil_name":  "PERFIL DEL SUELO 25M.xlsx",
        }


# ── Secuencias SPT ────────────────────────────────────────────────────────────
# Definición única de todos los valores N de campo.
# Clave = template_id de correlación ('1', '2', '3').
# 'opt1' → use_lower=True  |  'opt2' → use_lower=False.

_BASE3_OPT1 = [12, 16, 27, 34, 39, 45, 44, 48, 49, 52, 54, 57, 59, 62, 64]
_BASE3_OPT2 = [13, 17, 28, 35, 40, 46, 45, 49, 50, 53, 55, 58, 60, 63, 65]

SPT_SEQUENCES: Dict[str, Dict[str, List[int]]] = {
    "1": {
        "opt1": [6, 7, 14, 18, 22, 26, 28],
        "opt2": [7, 8, 15, 19, 23, 26, 29],
    },
    "2": {
        "opt1": [14, 19, 21, 28, 34, 37, 41, 44, 47, 50, 53, 56, 58, 61, 64, 67],
        "opt2": [15, 20, 22, 29, 35, 38, 42, 45, 48, 51, 54, 57, 59, 62, 65, 68],
    },
    "3": {
        "opt1": _BASE3_OPT1 + [64] * (25 - len(_BASE3_OPT1)),
        "opt2": _BASE3_OPT2 + [65] * (25 - len(_BASE3_OPT2)),
    },
}


def get_spt_values(correlation_template_id: str, use_lower: bool) -> List[str]:
    """Devuelve los valores SPT para la plantilla de correlación y el toggle indicados.

    Reemplaza la lógica duplicada en _calculate_spt_values y _get_legacy_n_campo_values.
    correlation_template_id: '1' (≤3 pisos), '2' (4-10), '3' (>10).
    """
    seqs = SPT_SEQUENCES.get(str(correlation_template_id), {})
    opt = seqs.get("opt1" if use_lower else "opt2", [])
    return [str(v) for v in opt]
