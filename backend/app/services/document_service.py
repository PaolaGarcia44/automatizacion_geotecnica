"""
Servicio de Documentos - Orquestación central de generación
"""

import logging
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from typing import List, Dict

from app.services.excel_service import excel_service
from app.utils.field_mapping import get_field_mapping
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """Servicio central para generación de documentos geotécnicos"""
    
    def __init__(self):
        self.excel_service = excel_service
        self.generated_dir = settings.GENERATED_DIR
    
    def validate_categoria(self, categoria: str) -> bool:
        """Valida que la categoría sea válida (1, 2 o 3)"""
        return categoria in ["1", "2", "3"]
    
    def validate_category_requirements(
        self,
        categoria: str,
        num_perforaciones: int,
        descripcion_proyecto: str,
    ) -> Dict[str, bool]:
        """
        Valida que el proyecto cumpla con los requisitos de su categoría
        
        Categoría 1: Hasta 3 pisos, 500 kN, mínimo 3 perforaciones, profundidad 6m
        Categoría 2: Hasta 10 pisos, 4000 kN, 4 perforaciones, profundidad 15m
        Categoría 3: Más de 10 pisos, >4000 kN, 4 perforaciones, profundidad 25m
        """
        requirements = {
            "valid": True,
            "categoria": categoria,
            "perforaciones_ok": False,
            "messages": [],
        }
        
        categoria_rules = {
            "1": {
                "min_perforaciones": 3,
                "description": "Categoría 1 (hasta 3 pisos): mínimo 3 perforaciones",
            },
            "2": {
                "min_perforaciones": 4,
                "description": "Categoría 2 (hasta 10 pisos): mínimo 4 perforaciones",
            },
            "3": {
                "min_perforaciones": 4,
                "description": "Categoría 3 (más de 10 pisos): mínimo 4 perforaciones",
            },
        }
        
        if categoria in categoria_rules:
            rule = categoria_rules[categoria]
            if num_perforaciones >= rule["min_perforaciones"]:
                requirements["perforaciones_ok"] = True
            else:
                requirements["valid"] = False
                requirements["messages"].append(
                    f"Perforaciones insuficientes. {rule['description']}, se tienen {num_perforaciones}."
                )
        
        return requirements
    
    def generate_documents(
        self,
        nombre_proyecto: str,
        municipio: str,
        fecha_registro: str,
        categoria: str,
        campo_n: str,
        perforaciones: List[Dict],
        descripcion: str = "",
        imagenes: List[str] = None,
    ) -> Dict:
        """
        Genera documentos Excel para un proyecto geotécnico
        
        Proceso:
        1. Validar entrada
        2. Generar ID de proyecto
        3. Crear datos de mapeo
        4. Generar Excel
        5. Retornar información de descarga
        """
        try:
            project_id = str(uuid4())[:8]
            timestamp = datetime.now().isoformat()
            
            # Validar categoría
            if not self.validate_categoria(categoria):
                return {
                    "success": False,
                    "message": f"Categoría inválida: {categoria}. Debe ser 1, 2 o 3.",
                    "project_id": None,
                }
            
            # Validar requisitos de categoría
            validation = self.validate_category_requirements(
                categoria=categoria,
                num_perforaciones=len(perforaciones) if perforaciones else 0,
                descripcion_proyecto=descripcion,
            )
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "message": "; ".join(validation["messages"]),
                    "project_id": project_id,
                }
            
            # Preparar datos para Excel
            excel_data = {
                "nombre_proyecto": nombre_proyecto,
                "municipio": municipio,
                "fecha_registro": fecha_registro,
                "categoria": categoria,
                "campo_n": campo_n,
                "descripcion": descripcion,
                "total_perforaciones": len(perforaciones) if perforaciones else 0,
            }
            
            # Generar archivo Excel
            logger.info(f"Iniciando generación de documentos para proyecto: {nombre_proyecto}")
            
            excel_file = self.excel_service.generate_excel(
                categoria=categoria,
                project_id=project_id,
                data=excel_data,
                perforaciones=perforaciones or [],
            )
            
            logger.info(f"Documentos generados exitosamente. Proyecto ID: {project_id}")
            
            # Preparar respuesta
            return {
                "success": True,
                "message": "Documentos generados exitosamente",
                "project_id": project_id,
                "files": [str(excel_file)],
                "timestamp": timestamp,
                "categoria": categoria,
                "nombre_proyecto": nombre_proyecto,
            }
            
        except Exception as e:
            logger.error(f"Error al generar documentos: {str(e)}")
            return {
                "success": False,
                "message": f"Error al generar documentos: {str(e)}",
                "project_id": None,
            }
    
    def get_available_templates_status(self) -> Dict:
        """Obtiene el estado de las plantillas disponibles"""
        return self.excel_service.verify_templates()


# Instancia global del servicio
document_service = DocumentService()
