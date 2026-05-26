"""
API Routes - Endpoints principales
"""

import logging
from fastapi import APIRouter, HTTPException, status
from datetime import date
from typing import List

from app.models.schemas import (
    DocumentGenerationRequest,
    DocumentGenerationResponse,
    PerforacionData,
)
from app.services.document_service import document_service
from app.services.template_service import template_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["documentos"])


@router.post(
    "/generate",
    response_model=DocumentGenerationResponse,
    summary="Generar documentos geotécnicos",
    description="Genera archivos Excel basados en datos del proyecto",
)
async def generate_documents(request: DocumentGenerationRequest) -> DocumentGenerationResponse:
    """
    Endpoint principal para generar documentos
    
    Recibe datos del proyecto y genera archivos Excel modificados
    basados en plantillas.
    """
    try:
        logger.info(f"Solicitud de generación recibida: {request.nombre_proyecto}")
        
        # Preparar perforaciones
        perforaciones = []
        if request.perforaciones:
            perforaciones = [
                {
                    "numero": p.numero,
                    "profundidad": p.profundidad,
                    "tipo_suelo": p.tipo_suelo or "",
                    "observaciones": p.observaciones or "",
                }
                for p in request.perforaciones
            ]
        
        # Llamar servicio de generación
        result = document_service.generate_documents(
            nombre_proyecto=request.nombre_proyecto,
            municipio=request.municipio,
            fecha_registro=request.fecha_registro.isoformat(),
            categoria=request.categoria,
            campo_n=request.campo_n,
            perforaciones=perforaciones,
            descripcion=request.descripcion or "",
            imagenes=request.imagenes,
        )
        
        return DocumentGenerationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error en endpoint /generate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar documentos: {str(e)}",
        )


@router.get(
    "/templates/status",
    summary="Estado de plantillas",
    description="Verifica qué plantillas están disponibles",
)
async def get_templates_status():
    """
    Retorna el estado de las plantillas disponibles
    """
    try:
        return {
            "status": "ok",
            "templates": document_service.get_available_templates_status(),
            "info": template_service.get_template_info(),
        }
    except Exception as e:
        logger.error(f"Error al obtener estado de plantillas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estado de plantillas: {str(e)}",
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Verifica que el backend está operativo",
)
async def health_check():
    """
    Endpoint de salud del servicio
    """
    return {
        "status": "healthy",
        "service": "AutoGeo Backend",
        "version": "1.0.0",
    }
