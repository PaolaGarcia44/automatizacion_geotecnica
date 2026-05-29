"""Field mappings for the geotechnical Excel templates.

The app writes into template_1.xlsx and template_2.xlsx, both using the same
core sheet layout:
- Primary sheet: P3
- Optional sheet: Parámetros / Parametros
"""

from __future__ import annotations

GENERAL_FIELD_MAPPING = {
    # Write the project name in C6 (short name). A5 will be used as a static label 'Parámetro:'
    "proyecto_ubicacion": ["C6"],
    # The client is intentionally not written into the plantilla A4 by default.
    # Template-specific code (e.g. LABORATORIO, CAPACIDAD) writes client where needed.
    # Static label on the primary sheet
    "parametro_label": ["A5"],
    "fecha_registro": ["C7"],
    "sondeo": ["A9"],
    "peso_martinete": ["G7"],
    "altura_caida": ["G8"],
    "nivel_freatico": ["I8"],
}

PERFORACION_MAPPING = {
    "tabla_inicio_row": 10,
    "allowed_columns": {
        "profundidad_z": "A",
        "gamma": "B",
        "n_campo_spt": "F",
        "cohesion_c": "O",
        "descripcion_suelo": "Q",
    },
}

PARAMETROS_MAPPING = {
    "tabla_inicio_row": 10,
    "allowed_columns": {
        "rango_profundidad": "A",
        "gamma": "B",
        "c": "C",
        "phi": "D",
        "nu": "G",
        "e": "H",
        "unidad_geologica": "I",
    },
}


def get_field_mapping(template_id: str) -> dict:
    """Return the same field mapping for both templates."""
    return GENERAL_FIELD_MAPPING


def get_perforacion_mapping(template_id: str) -> dict:
    """Return the perforation mapping used by both templates."""
    return PERFORACION_MAPPING


def get_parametros_mapping(template_id: str) -> dict:
    """Return the optional parameters mapping used by both templates."""
    return PARAMETROS_MAPPING
