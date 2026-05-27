from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class PerforacionData(BaseModel):
    """Datos de una fila de sondeo/perforación."""

    profundidad_z: float = Field(..., description="Profundidad Z en metros")
    gamma: float = Field(..., description="Peso específico gamma en kN/m³")
    n_campo_spt: int = Field(..., description="N de campo SPT")
    cohesion_c: Optional[float] = Field(None, description="Cohesión C' en kPa")
    descripcion_suelo: str = Field(..., description="Descripción del suelo")


class ParametroRangoData(BaseModel):
    """Fila opcional de parámetros por rango de profundidad."""

    rango_profundidad: str = Field(..., description="Ejemplo: 0.00 - 1.00")
    gamma: Optional[float] = None
    c: Optional[float] = None
    phi: Optional[float] = None
    nu: Optional[float] = None
    e: Optional[float] = None
    unidad_geologica: Optional[str] = None


class DocumentGenerationRequest(BaseModel):
    """Solicitud para generar documentos geotécnicos."""

    template_id: Optional[str] = Field(None, description="Plantilla a usar: 1 o 2 (opcional, backend puede decidir)")
    proyecto_ubicacion: str = Field(..., min_length=3, description="Proyecto + ubicación")
    fecha_registro: date = Field(..., description="Fecha del registro")
    pisos: int = Field(..., description="Número de pisos del proyecto")
    sondeo: Optional[str] = Field('P-1', description="Nombre del sondeo, ej. P-1")
    peso_martinete: Optional[float] = Field(63.5, description="Peso del martinete")
    altura_caida: Optional[float] = Field(0.76, description="Altura de caída")
    nivel_freatico: Optional[Union[str, float]] = Field("N.A.", description="Nivel freático o N.A.")
    perforaciones: List[PerforacionData] = Field(default_factory=list)
    parametros: List[ParametroRangoData] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "template_id": "1",
                "proyecto_ubicacion": "Proyecto Centro Medellín - Zona Norte",
                "fecha_registro": "2024-05-25",
                "sondeo": "P-1",
                "peso_martinete": 63.5,
                "altura_caida": 0.76,
                "nivel_freatico": "N.A.",
                "perforaciones": [
                    {
                        "profundidad_z": 0.0,
                        "gamma": 18.2,
                        "n_campo_spt": 12,
                        "cohesion_c": 5.0,
                        "descripcion_suelo": "Arena limosa",
                    }
                ],
                "parametros": [
                    {
                        "rango_profundidad": "0.00 - 1.00",
                        "gamma": 18.2,
                        "c": 5.0,
                        "phi": 28.0,
                        "nu": 0.30,
                        "e": 12000,
                        "unidad_geologica": "Relleno granular",
                    }
                ],
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
