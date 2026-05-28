import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración global de la aplicación"""
    
    # Rutas base
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    GENERATED_DIR: Path = BASE_DIR / "generated"
    EXCEL_TEMPLATES_DIR: Path = TEMPLATES_DIR / "excel"
    WORD_TEMPLATES_DIR: Path = TEMPLATES_DIR / "word"
    IMAGES_UPLOAD_DIR: Path = GENERATED_DIR / "images"
    
    # Configuración FastAPI
    APP_NAME: str = "AutoGeo Backend - Automatización Documental Geotécnica"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    # WARNING: during development we allow all origins to avoid CORS issues.
    # Make this more restrictive in production.
    ALLOWED_ORIGINS: list = ["*"]
    
    # Configuración de archivos
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = ["xlsx", "xls", "docx", "pdf", "jpg", "jpeg", "png", "gif"]
    
    # Plantillas Excel disponibles
    TEMPLATES_CONFIG: dict = {
        "1": "plantilla_1.xlsx",
        "2": "plantilla_2.xlsx",
        "3": "plantilla_3.xlsx",
        "4": "LABORATORIO - FORMULAS 1.xlsx",
        "5": "LABORATORIO - FORMULAS 2.xlsx",
        "6": "LABORATORIO - FORMULAS 3.xlsx",
        "7": "LABORATORIO - FORMULAS 4.xlsx",
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()

# Crear directorios si no existen
settings.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
settings.IMAGES_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
