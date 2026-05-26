"""
Field Mapping - Mapeo centralizado de campos dinámicos a celdas Excel

Cada plantilla tiene sus propias celdas donde se deben modificar los datos.
Este archivo centraliza todos los mapeos para fácil mantenimiento.
"""

# Mapeo de campos para Categoría 1
FIELD_MAPPING_CATEGORIA_1 = {
    "nombre_proyecto": ["B5", "D10", "F2"],
    "municipio": ["C7", "E12"],
    "fecha_registro": ["H3", "B15"],
    "campo_n": ["C5"],
    "descripcion": ["A20:F25"],  # Rango para descripción
    "categoria": ["B3"],
    "total_perforaciones": ["C8"],
}

# Mapeo de campos para Categoría 2
FIELD_MAPPING_CATEGORIA_2 = {
    "nombre_proyecto": ["B4", "E10"],
    "municipio": ["C6", "F12"],
    "fecha_registro": ["G2", "B14"],
    "campo_n": ["B5"],
    "descripcion": ["A18:E22"],
    "categoria": ["A3"],
    "total_perforaciones": ["D8"],
}

# Mapeo de campos para Categoría 3
FIELD_MAPPING_CATEGORIA_3 = {
    "nombre_proyecto": ["B3", "D8"],
    "municipio": ["C5"],
    "fecha_registro": ["H2"],
    "campo_n": ["A4"],
    "descripcion": ["A16:F20"],
    "categoria": ["C2"],
    "total_perforaciones": ["B7"],
}

# Mapeo de perforaciones por tabla
# Cada categoría puede tener un formato diferente para registrar perforaciones
PERFORACION_MAPPING_CATEGORIA_1 = {
    "tabla_inicio_row": 27,  # Fila donde comienza la tabla de perforaciones
    "numero_col": "A",
    "profundidad_col": "B",
    "tipo_suelo_col": "C",
    "observaciones_col": "D",
    "max_perforaciones": 10,
}

PERFORACION_MAPPING_CATEGORIA_2 = {
    "tabla_inicio_row": 24,
    "numero_col": "A",
    "profundidad_col": "B",
    "tipo_suelo_col": "C",
    "observaciones_col": "D",
    "max_perforaciones": 15,
}

PERFORACION_MAPPING_CATEGORIA_3 = {
    "tabla_inicio_row": 25,
    "numero_col": "A",
    "profundidad_col": "B",
    "tipo_suelo_col": "C",
    "observaciones_col": "D",
    "max_perforaciones": 20,
}

# Mapeo general por categoría
FIELD_MAPPINGS = {
    "1": FIELD_MAPPING_CATEGORIA_1,
    "2": FIELD_MAPPING_CATEGORIA_2,
    "3": FIELD_MAPPING_CATEGORIA_3,
}

PERFORACION_MAPPINGS = {
    "1": PERFORACION_MAPPING_CATEGORIA_1,
    "2": PERFORACION_MAPPING_CATEGORIA_2,
    "3": PERFORACION_MAPPING_CATEGORIA_3,
}


def get_field_mapping(categoria: str) -> dict:
    """Obtiene el mapeo de campos para una categoría"""
    return FIELD_MAPPINGS.get(str(categoria), {})


def get_perforacion_mapping(categoria: str) -> dict:
    """Obtiene el mapeo de perforaciones para una categoría"""
    return PERFORACION_MAPPINGS.get(str(categoria), {})
