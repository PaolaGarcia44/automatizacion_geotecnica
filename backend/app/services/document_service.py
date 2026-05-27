"""Document orchestration service for the two Excel templates."""

import logging
from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Optional

from app.services.excel_service import excel_service

logger = logging.getLogger(__name__)


class DocumentService:
    """Central service for generating geotechnical Excel files."""
    
    def __init__(self):
        self.excel_service = excel_service
    
    def generate_documents(
        self,
        proyecto_ubicacion: str,
        fecha_registro,
        pisos: int,
        perforaciones: Optional[List[Dict]] = None,
        parametros: Optional[List[Dict]] = None,
    ) -> Dict:
        """Generate the Excel file from the selected template."""        
        try:
            project_id = str(uuid4())[:8]
            timestamp = datetime.now().isoformat()

            perforaciones_to_use = perforaciones or []

            # Decide plantilla y perforaciones por defecto según número de pisos
            nPisos = int(pisos or 0)
            # Default mappings:
            # <=3 pisos -> plantilla 1, 3 perforaciones de 6 m
            # 4..10 pisos -> plantilla 2, 4 perforaciones de 15 m
            # >10 -> plantilla 2, 4 perforaciones de 15 m
            if not perforaciones_to_use and nPisos <= 3:
                selected_template = '1'
                default_perforaciones = [
                    {"profundidad_z": 6, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                    {"profundidad_z": 6, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                    {"profundidad_z": 6, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                ]
            elif not perforaciones_to_use:
                selected_template = '2'
                default_perforaciones = [
                    {"profundidad_z": 15, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                    {"profundidad_z": 15, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                    {"profundidad_z": 15, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                    {"profundidad_z": 15, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                ]
            else:
                selected_template = '1' if nPisos <= 3 else '2'
                default_perforaciones = perforaciones_to_use

            # Only write Proyecto and Fecha to the template; leave all other cells unchanged
            excel_data = {
                "proyecto_ubicacion": proyecto_ubicacion,
                "fecha_registro": fecha_registro,
            }

            logger.info("Iniciando generación de documentos para proyecto: %s", proyecto_ubicacion)

            excel_file = self.excel_service.generate_excel(
                template_id=selected_template,
                project_id=project_id,
                data=excel_data,
                perforaciones=default_perforaciones,
                parametros=parametros or [],
            )

            logger.info("Documentos generados exitosamente. Proyecto ID: %s", project_id)

            return {
                "success": True,
                "message": "Documentos generados exitosamente",
                "project_id": project_id,
                "files": [str(excel_file)],
                "download_url": f"/api/download/{excel_file.name}",
                "timestamp": timestamp,
                "template_id": selected_template,
                "proyecto_ubicacion": proyecto_ubicacion,
            }

        except Exception as e:
            logger.error("Error al generar documentos: %s", str(e))
            return {
                "success": False,
                "message": f"Error al generar documentos: {str(e)}",
                "project_id": None,
            }

    def get_available_templates_status(self) -> Dict:
        """Get the status of the configured templates."""
        return self.excel_service.verify_templates()


# Instancia global del servicio
document_service = DocumentService()
