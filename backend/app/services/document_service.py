"""Document orchestration service for the Excel templates."""

import logging
from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Optional
import re
import unicodedata
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from app.core.config import settings
from app.services.excel_service import excel_service

logger = logging.getLogger(__name__)


class DocumentService:
    """Central service for generating geotechnical Excel files."""
    
    def __init__(self):
        self.excel_service = excel_service

    def _slugify_filename(self, value: str, fallback: str) -> str:
        text = unicodedata.normalize("NFD", value or "").encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")
        return text or fallback
    
    def generate_documents(
        self,
        proyecto_ubicacion: str,
        cliente: Optional[str],
        fecha_registro,
        pisos: int,
        perforaciones: Optional[List[Dict]] = None,
        parametros: Optional[List[Dict]] = None,
        template_id: Optional[str] = None,
        template_ids: Optional[List[str]] = None,
    ) -> Dict:
        """Generate the Excel file from the selected template."""        
        try:
            project_id = str(uuid4())[:8]
            timestamp = datetime.now().isoformat()

            perforaciones_to_use = perforaciones or []

            # Decide plantilla and defaults either from an explicit template_id or from pisos.
            nPisos = int(pisos or 0)
            requested_template = str(template_id).strip() if template_id is not None and str(template_id).strip() else None

            def _default_perforaciones_for_template(template_key: str) -> List[Dict]:
                if template_key == '1':
                    return [
                        {"profundidad_z": 6, "gamma": 15, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                        {"profundidad_z": 6, "gamma": 16, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                        {"profundidad_z": 6, "gamma": 17, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                    ]
                if template_key in {'2', '3'}:
                    return [
                        {"profundidad_z": 15, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                        {"profundidad_z": 15, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                        {"profundidad_z": 15, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                        {"profundidad_z": 15, "gamma": None, "n_campo_spt": 0, "cohesion_c": None, "descripcion_suelo": ""},
                    ]
                return []

            if requested_template in {'1', '2', '3'}:
                selected_template = requested_template
                default_perforaciones = perforaciones_to_use or _default_perforaciones_for_template(selected_template)
            elif requested_template == '8':
                selected_template = requested_template
                default_perforaciones = perforaciones_to_use
            elif requested_template in {'4', '5', '6'}:
                selected_template = requested_template
                default_perforaciones = perforaciones_to_use
            elif not perforaciones_to_use:
                selected_template = '8'
                default_perforaciones = perforaciones_to_use
            else:
                selected_template = '8'
                default_perforaciones = perforaciones_to_use

            # If the user provided soil menu values, keep the visible text focused on
            # the soil type; the predominant color will be rendered as cell fill.
            for row_data in default_perforaciones:
                tipo_suelo = row_data.get('tipo_suelo_principal')
                descripcion_suelo = row_data.get('descripcion_suelo')

                if not descripcion_suelo:
                    row_data['descripcion_suelo'] = str(tipo_suelo or '').strip()

            # Fill gamma values sequentially when they are missing.
            # The first soil layer starts at 15 and each additional layer increments by 1.
            # This applies to all templates so the gamma column stays aligned with the
            # number of layers the user entered from the soil menus.
            for index, row_data in enumerate(default_perforaciones):
                if row_data.get('gamma') in (None, ''):
                    row_data['gamma'] = 15 + index

            # Only write Proyecto and Fecha to the template; leave all other cells unchanged
            # Force proyecto_ubicacion to uppercase for the copy
            proyecto_upper = proyecto_ubicacion.upper() if isinstance(proyecto_ubicacion, str) else proyecto_ubicacion

            # Calculate fecha_registro + 20 days for cell C7. Support date or ISO string inputs.
            from datetime import date, timedelta

            fecha_obj = None
            if isinstance(fecha_registro, date) and not isinstance(fecha_registro, datetime):
                fecha_obj = fecha_registro
            elif isinstance(fecha_registro, datetime):
                fecha_obj = fecha_registro.date()
            elif isinstance(fecha_registro, str):
                try:
                    fecha_obj = datetime.fromisoformat(fecha_registro).date()
                except Exception:
                    try:
                        fecha_obj = date.fromisoformat(fecha_registro)
                    except Exception:
                        fecha_obj = None

            fecha_c7 = None
            if fecha_obj:
                fecha_c7 = fecha_obj + timedelta(days=20)

            excel_data = {
                "proyecto_ubicacion": proyecto_upper,
                "cliente_display": f"Cliente: {cliente}" if cliente else None,
                "fecha_registro": fecha_c7 if fecha_c7 is not None else fecha_registro,
                "fecha_registro_original": fecha_obj if fecha_obj is not None else fecha_registro,
                "cliente": cliente,
                "pisos": nPisos,
                # static label required by UI: A5 should read 'Parámetro:'
                "parametro_label": "Parámetro:",
            }

            requested_templates = [str(item).strip() for item in (template_ids or []) if str(item).strip()]
            if requested_templates:
                # Batch mode: include the capacity template, the correlation template
                # for the floor range, plus the LABORATORIO set.
                capacity_template_id = '8'
                correlation_template_id = '1' if nPisos <= 3 else '2' if nPisos <= 10 else '3'
                laboratorio_template_ids = ['4', '5', '6'] if nPisos <= 3 else ['4', '5', '6', '7']
                batch_templates = [capacity_template_id, correlation_template_id, *laboratorio_template_ids]

                client_slug = self._slugify_filename(str(cliente or '').strip(), 'cliente')
                project_slug = self._slugify_filename(proyecto_upper, 'proyecto')
                zip_base_name = f"{client_slug} - {project_slug}.zip"
                zip_path = self.excel_service.generated_dir / zip_base_name

                output_files = []
                with ZipFile(zip_path, 'w', compression=ZIP_DEFLATED) as zip_file:
                    for current_template in batch_templates:
                        generated_file = self.excel_service.generate_excel(
                            template_id=current_template,
                            project_id=project_id,
                            data=excel_data,
                            perforaciones=default_perforaciones,
                            parametros=parametros or [],
                        )
                        output_files.append(generated_file)

                        # Map known templates to friendly names inside the ZIP
                        archive_name_map = {
                            '1': 'CORRELACIÓN GEOTÉCNICA DE PARÁMETROS GEOMECÁNICOS.xlsx',
                            '2': 'CORRELACIÓN GEOTÉCNICA DE PARÁMETROS GEOMECÁNICOS.xlsx',
                            '3': 'CORRELACIÓN GEOTÉCNICA DE PARÁMETROS GEOMECÁNICOS.xlsx',
                            '4': 'LABORATORIO - FORMULAS 1.xlsx',
                            '5': 'LABORATORIO - FORMULAS 2.xlsx',
                            '6': 'LABORATORIO - FORMULAS 3.xlsx',
                            '7': 'LABORATORIO - FORMULAS 4.xlsx',
                        }

                        # The capacity workbook should keep its real filename inside the ZIP.
                        if str(current_template) == str(capacity_template_id):
                            archive_name = settings.TEMPLATES_CONFIG.get(str(current_template), generated_file.name)
                        else:
                            archive_name = archive_name_map.get(
                                str(current_template),
                                settings.TEMPLATES_CONFIG.get(str(current_template), generated_file.name),
                            )

                        zip_file.write(generated_file, arcname=archive_name)

                return {
                    "success": True,
                    "message": "Documentos generados exitosamente en paquete ZIP",
                    "project_id": project_id,
                    "files": [str(file_path) for file_path in output_files] + [str(zip_path)],
                    "download_url": f"/api/download/{zip_path.name}",
                    "timestamp": timestamp,
                    "template_id": ",".join(batch_templates),
                    "proyecto_ubicacion": proyecto_upper,
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
                "proyecto_ubicacion": proyecto_upper,
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
