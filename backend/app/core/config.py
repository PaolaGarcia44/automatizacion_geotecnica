import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings


def _resolve_base_dir() -> Path:
    """
    Resuelve el directorio base correctamente tanto en desarrollo
    como cuando el backend está empaquetado con PyInstaller.

    En PyInstaller (modo one-folder), sys.executable apunta al .exe
    dentro de la carpeta de distribución, que es donde también están
    las plantillas y los archivos generados.
    """
    if getattr(sys, 'frozen', False):
        # Modo PyInstaller: el exe está en dist/autogeo_backend/
        return Path(sys.executable).parent
    # Modo desarrollo: backend/app/core/config.py → 3 niveles arriba = backend/
    return Path(__file__).resolve().parent.parent.parent


_BASE = _resolve_base_dir()


def _resolve_generated_dir() -> Path:
    """
    En modo empaquetado usa AppData para poder escribir archivos
    aunque la app esté instalada en Program Files.
    """
    if getattr(sys, 'frozen', False):
        appdata = Path(os.environ.get('APPDATA', str(Path.home())))
        gen_dir = appdata / 'AutoGeo' / 'generated'
        gen_dir.mkdir(parents=True, exist_ok=True)
        return gen_dir
    return _BASE / 'generated'


class Settings(BaseSettings):
    """Configuración global de la aplicación"""

    # Rutas base
    BASE_DIR: Path = _BASE
    TEMPLATES_DIR: Path = _BASE / 'templates'
    GENERATED_DIR: Path = _resolve_generated_dir()
    EXCEL_TEMPLATES_DIR: Path = _BASE / 'templates' / 'excel'
    WORD_TEMPLATES_DIR: Path = _BASE / 'templates' / 'word'
    IMAGES_UPLOAD_DIR: Path = _resolve_generated_dir() / 'images'

    # Configuración FastAPI
    APP_NAME: str = 'AutoGeo Backend - Automatización Documental Geotécnica'
    APP_VERSION: str = '1.0.0'
    DEBUG: bool = True

    # CORS — permite localhost para dev y app:// para Electron
    ALLOWED_ORIGINS: list = ['*']

    # Configuración de archivos
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = ['xlsx', 'xls', 'docx', 'pdf', 'jpg', 'jpeg', 'png', 'gif']

    # Plantillas Excel disponibles
    TEMPLATES_CONFIG: dict = {
        '1': 'plantilla_1.xlsx',
        '2': 'plantilla_2.xlsx',
        '3': 'plantilla_3.xlsx',
        '8': 'CAPACIDAD PORTANTE CASA.xlsx',
        '9': 'INCONFINADO.xlsx',
        '10': 'ASENTAMIENTOS ZAPATAS 300.xlsx',
        '11': 'ASENTAMIENTOS ZAPATAS 800.xlsx',
        '12': 'P-1.xls',
        '13': 'P-2.xls',
        '14': 'P-3.xls',
        '15': 'P-4.xls',
        '4': 'LABORATORIO - FORMULAS 1.xlsx',
        '5': 'LABORATORIO - FORMULAS 2.xlsx',
        '6': 'LABORATORIO - FORMULAS 3.xlsx',
        '7': 'LABORATORIO - FORMULAS 4.xlsx',
    }

    class Config:
        env_file = '.env'
        case_sensitive = True


# Instancia global de configuración
settings = Settings()

# Crear directorios si no existen
settings.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
(settings.GENERATED_DIR / 'images').mkdir(parents=True, exist_ok=True)
