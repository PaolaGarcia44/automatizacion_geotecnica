"""
Servicio de Plantillas - Gestión centralizada de templates
"""

import logging
from pathlib import Path
from typing import List, Dict

from app.core.config import settings

logger = logging.getLogger(__name__)


class TemplateService:
    """Servicio para gestionar plantillas Excel y Word"""
    
    def __init__(self):
        self.excel_templates_dir = settings.EXCEL_TEMPLATES_DIR
        self.word_templates_dir = settings.WORD_TEMPLATES_DIR
    
    def get_available_excel_templates(self) -> List[str]:
        """Obtiene la lista de plantillas Excel disponibles"""
        try:
            templates = [f.name for f in self.excel_templates_dir.glob("*.xlsx")]
            logger.info(f"Plantillas Excel encontradas: {len(templates)}")
            return templates
        except Exception as e:
            logger.error(f"Error al obtener plantillas Excel: {str(e)}")
            return []
    
    def get_available_word_templates(self) -> List[str]:
        """Obtiene la lista de plantillas Word disponibles"""
        try:
            templates = [f.name for f in self.word_templates_dir.glob("*.docx")]
            logger.info(f"Plantillas Word encontradas: {len(templates)}")
            return templates
        except Exception as e:
            logger.error(f"Error al obtener plantillas Word: {str(e)}")
            return []
    
    def get_template_info(self) -> Dict:
        """Obtiene información de todas las plantillas disponibles"""
        return {
            "excel_templates": self.get_available_excel_templates(),
            "word_templates": self.get_available_word_templates(),
            "excel_count": len(self.get_available_excel_templates()),
            "word_count": len(self.get_available_word_templates()),
        }


# Instancia global del servicio
template_service = TemplateService()
