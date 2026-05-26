"""
FastAPI Main Application

Servidor backend para AutoGeo - Automatización Documental Geotécnica

Stack:
- FastAPI
- Uvicorn
- openpyxl
- pandas
- python-docx
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.documents import router as documents_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para generación automatizada de documentos geotécnicos con Excel y Word",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(documents_router)


# Eventos del ciclo de vida
@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    logger.info("=" * 60)
    logger.info("AutoGeo Backend iniciado")
    logger.info(f"Ambiente: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"Directorio de plantillas: {settings.EXCEL_TEMPLATES_DIR}")
    logger.info(f"Directorio de salida: {settings.GENERATED_DIR}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento al cerrar la aplicación"""
    logger.info("AutoGeo Backend cerrado")


# Rutas raíz
@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "AutoGeo Backend - Automatización Documental Geotécnica",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Manejo de excepciones global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Excepción global: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "error": str(exc) if settings.DEBUG else "Error interno",
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
