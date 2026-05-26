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
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Configuración de archivos
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = ["xlsx", "xls", "docx", "pdf", "jpg", "jpeg", "png", "gif"]
    
    # Rutas de plantillas disponibles
    TEMPLATES_CONFIG: dict = {
        "Categoria1": "plantilla_categoria_1.xlsx",
        "Categoria2": "plantilla_categoria_2.xlsx",
        "Categoria3": "plantilla_categoria_3.xlsx",
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()

# Crear directorios si no existen
settings.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
settings.IMAGES_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
