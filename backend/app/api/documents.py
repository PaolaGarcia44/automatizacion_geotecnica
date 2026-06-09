"""API routes for Excel generation and download."""

import logging
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Form, File, UploadFile
import json
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
async def generate_documents(
    proyecto_ubicacion: str = Form(...),
    cliente: Optional[str] = Form(None),
    fecha_registro: str = Form(...),
    sondeo: Optional[str] = Form(None),
    pisos: int = Form(...),
    perforaciones: str = Form('[]'),
    parametros: str = Form('[]'),
    template_id: Optional[str] = Form(None),
    template_ids: Optional[str] = Form(None),
    clasificacion_suelo: Optional[str] = Form(None),
    clasificaciones_por_lab: Optional[str] = Form(None),
    files: list[UploadFile] | None = File(None),
) -> DocumentGenerationResponse:
    try:
        logger.info("Solicitud de generación recibida: %s", proyecto_ubicacion)

        try:
            perf_list = json.loads(perforaciones) if isinstance(perforaciones, str) else perforaciones
        except Exception:
            perf_list = []

        try:
            parametros_list = json.loads(parametros) if isinstance(parametros, str) else parametros
        except Exception:
            parametros_list = []

        # Save uploaded images to a project folder inside GENERATED_DIR
        project_id = None
        images_dir = None
        try:
            project_id = str(uuid4())[:8]
            images_dir = settings.GENERATED_DIR / f"{project_id}" / "imagenes"
            if files:
                images_dir.mkdir(parents=True, exist_ok=True)
                for upload in files:
                    target = images_dir / Path(upload.filename).name
                    with target.open('wb') as out_f:
                        content = await upload.read()
                        out_f.write(content)
        except Exception:
            logger.debug('No se pudieron guardar imágenes subidas', exc_info=True)

        clf_por_lab = None
        if clasificaciones_por_lab:
            try:
                clf_por_lab = json.loads(clasificaciones_por_lab)
            except Exception:
                clf_por_lab = None

        result = document_service.generate_documents(
            template_id=template_id,
            template_ids=json.loads(template_ids) if template_ids else None,
            proyecto_ubicacion=proyecto_ubicacion,
            cliente=cliente,
            fecha_registro=fecha_registro,
            sondeo=sondeo,
            pisos=pisos,
            perforaciones=perf_list,
            parametros=parametros_list,
            images_dir=images_dir,
            project_id=project_id,
            clasificacion_suelo=clasificacion_suelo or None,
            clasificaciones_por_lab=clf_por_lab,
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

    if not file_path.exists() or file_path.suffix.lower() not in {".xlsx", ".xls", ".zip"}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if file_path.suffix.lower() == ".xls":
        media_type = "application/vnd.ms-excel"
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
