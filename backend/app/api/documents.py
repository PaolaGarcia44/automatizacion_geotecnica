"""API routes for Excel generation and download."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.models.schemas import (
    DocumentGenerationRequest,
    DocumentGenerationResponse,
)
from app.services.document_service import document_service
from app.services.template_service import template_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["documentos"])


@router.post(
    "/generate",
    response_model=DocumentGenerationResponse,
    summary="Generate geotechnical Excel",
    description="Generate an Excel file from one of the two templates",
)
async def generate_documents(request: DocumentGenerationRequest) -> DocumentGenerationResponse:
    try:
        logger.info("Solicitud de generación recibida: %s", request.proyecto_ubicacion)
        # Debug: log full incoming payload (useful to diagnose 422/CORS issues)
        try:
            logger.debug("Payload: %s", request.model_dump())
        except Exception:
            logger.debug("Payload: (no se pudo serializar el modelo)")

        # Backend decides template and generates default perforaciones based on 'pisos'
        parametros = [p.model_dump() for p in request.parametros]

        result = document_service.generate_documents(
            template_id=request.template_id,
            template_ids=request.template_ids,
            proyecto_ubicacion=request.proyecto_ubicacion,
            fecha_registro=request.fecha_registro,
            pisos=request.pisos,
            perforaciones=[p.model_dump() for p in request.perforaciones],
            parametros=parametros,
        )

        return DocumentGenerationResponse(**result)

    except Exception as e:
        logger.error("Error en endpoint /generate: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar documentos: {str(e)}",
        )


@router.get(
    "/download/{filename}",
    summary="Download generated Excel",
    description="Download a generated Excel file from the server",
)
async def download_excel(filename: str):
    safe_name = Path(filename).name
    file_path = settings.GENERATED_DIR / safe_name

    if not file_path.exists() or file_path.suffix.lower() not in {".xlsx", ".zip"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if file_path.suffix.lower() == ".zip":
        media_type = "application/zip"

    return FileResponse(
        path=str(file_path),
        filename=safe_name,
        media_type=media_type,
    )


@router.get(
    "/templates/status",
    summary="Estado de plantillas",
    description="Verifica qué plantillas están disponibles",
)
async def get_templates_status():
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
    return {
        "status": "healthy",
        "service": "AutoGeo Backend",
        "version": "1.0.0",
    }
