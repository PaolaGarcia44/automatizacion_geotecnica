from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class PerforacionData(BaseModel):
    """Datos de perforación individual"""
    numero: int = Field(..., description="Número de perforación")
    profundidad: float = Field(..., description="Profundidad en metros")
    tipo_suelo: Optional[str] = None
    observaciones: Optional[str] = None


class DocumentGenerationRequest(BaseModel):
    """Solicitud para generar documentos geotécnicos"""
    nombre_proyecto: str = Field(..., min_length=3, description="Nombre del proyecto")
    municipio: str = Field(..., min_length=2, description="Municipio donde se realizará el proyecto")
    fecha_registro: date = Field(..., description="Fecha de registro del proyecto")
    categoria: str = Field(..., description="Categoría del proyecto (1, 2 o 3)")
    campo_n: str = Field(..., description="Campo N del proyecto")
    descripcion: Optional[str] = None
    perforaciones: List[PerforacionData] = Field(default_factory=list)
    imagenes: Optional[List[str]] = Field(default_factory=list, description="URLs o rutas de imágenes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre_proyecto": "Estudio Geotécnico Centro Medellín",
                "municipio": "Medellín",
                "fecha_registro": "2024-05-25",
                "categoria": "1",
                "campo_n": "Suelo tipo C",
                "descripcion": "Análisis preliminar de suelos",
                "perforaciones": [
                    {"numero": 1, "profundidad": 6.0, "tipo_suelo": "Arena"},
                    {"numero": 2, "profundidad": 8.5, "tipo_suelo": "Arcilla"},
                ],
                "imagenes": [],
            }
        }
    }


class DocumentGenerationResponse(BaseModel):
    """Respuesta de generación de documentos"""
    success: bool
    message: str
    project_id: Optional[str] = None
    files: Optional[List[str]] = None
    download_url: Optional[str] = None
    timestamp: Optional[str] = None


class CategoryRule(BaseModel):
    """Reglas por categoría"""
    category: int
    max_floors: int
    max_load_kN: float
    min_perforaciones: int
    min_profundidad_m: float
