"""
Servicio de Excel - Manejo de plantillas y generación de archivos

Este servicio:
1. Copia plantillas originales (nunca las modifica)
2. Modifica solo las celdas dinámicas necesarias
3. Conserva fórmulas, estilos y diseño original
4. Maneja perforaciones en tablas
"""

import shutil
from pathlib import Path
from datetime import date
from typing import Optional, List
import openpyxl
from openpyxl.utils import get_column_letter
import logging

from app.utils.field_mapping import get_field_mapping, get_perforacion_mapping
from app.core.config import settings

logger = logging.getLogger(__name__)


class ExcelService:
    """Servicio centralizado para operaciones con Excel"""
    
    def __init__(self):
        self.templates_dir = settings.EXCEL_TEMPLATES_DIR
        self.generated_dir = settings.GENERATED_DIR
    
    def _get_template_path(self, categoria: str) -> Path:
        """Obtiene la ruta de la plantilla para una categoría"""
        template_filename = settings.TEMPLATES_CONFIG.get(f"Categoria{categoria}", f"plantilla_categoria_{categoria}.xlsx")
        template_path = self.templates_dir / template_filename
        
        if not template_path.exists():
            raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
        
        return template_path
    
    def _copy_template(self, categoria: str, project_id: str) -> Path:
        """
        Copia la plantilla a un nuevo archivo de trabajo
        
        IMPORTANTE: Las plantillas NUNCA se modifican directamente.
        Se crea una copia para cada proyecto.
        """
        try:
            template_path = self._get_template_path(categoria)
            output_filename = f"{project_id}_categoria_{categoria}.xlsx"
            output_path = self.generated_dir / output_filename
            
            # Copiar plantilla original
            shutil.copy2(template_path, output_path)
            logger.info(f"Plantilla copiada: {template_path} → {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"Error al copiar plantilla: {str(e)}")
            raise
    
    def _set_cell_value(self, ws, cell_ref: str, value):
        """
        Establece el valor de una celda preservando el tipo de dato
        
        Soporta:
        - Celdas individuales: "B5"
        - Rangos: "A20:F25" (establece en A20)
        """
        try:
            if ":" in cell_ref:
                # Es un rango, usar la primera celda
                cell_ref = cell_ref.split(":")[0]
            
            cell = ws[cell_ref]
            cell.value = value
            logger.debug(f"Celda {cell_ref} actualizada: {value}")
            
        except Exception as e:
            logger.error(f"Error al establecer valor en {cell_ref}: {str(e)}")
            raise
    
    def _add_perforaciones(self, ws, perforaciones: List[dict], categoria: str):
        """
        Añade datos de perforaciones a la tabla en Excel
        
        Preserva el formato y rellena las filas de la tabla.
        """
        if not perforaciones:
            return
        
        perf_mapping = get_perforacion_mapping(categoria)
        start_row = perf_mapping["tabla_inicio_row"]
        max_perf = perf_mapping["max_perforaciones"]
        
        numero_col = perf_mapping["numero_col"]
        profundidad_col = perf_mapping["profundidad_col"]
        tipo_suelo_col = perf_mapping["tipo_suelo_col"]
        observaciones_col = perf_mapping["observaciones_col"]
        
        try:
            for idx, perforacion in enumerate(perforaciones[:max_perf]):
                row = start_row + idx
                
                # Establecer valores
                self._set_cell_value(ws, f"{numero_col}{row}", perforacion.get("numero", idx + 1))
                self._set_cell_value(ws, f"{profundidad_col}{row}", perforacion.get("profundidad", 0))
                self._set_cell_value(ws, f"{tipo_suelo_col}{row}", perforacion.get("tipo_suelo", ""))
                self._set_cell_value(ws, f"{observaciones_col}{row}", perforacion.get("observaciones", ""))
            
            logger.info(f"Perforaciones añadidas: {len(perforaciones[:max_perf])}")
            
        except Exception as e:
            logger.error(f"Error al añadir perforaciones: {str(e)}")
            raise
    
    def generate_excel(
        self,
        categoria: str,
        project_id: str,
        data: dict,
        perforaciones: List[dict] = None,
    ) -> Path:
        """
        Genera un archivo Excel modificado con los datos del proyecto
        
        Proceso:
        1. Copia la plantilla original
        2. Abre la copia
        3. Modifica solo las celdas necesarias
        4. Conserva fórmulas y estilos
        5. Guarda el archivo
        """
        try:
            # Paso 1: Copiar plantilla
            work_file = self._copy_template(categoria, project_id)
            
            # Paso 2: Abrir la copia
            workbook = openpyxl.load_workbook(work_file)
            worksheet = workbook.active
            
            # Paso 3: Obtener mapeo de campos
            field_mapping = get_field_mapping(categoria)
            
            # Paso 4: Modificar campos dinámicos
            for field_name, cell_refs in field_mapping.items():
                if field_name in data and data[field_name] is not None:
                    value = data[field_name]
                    
                    # Si es una fecha, convertir a string
                    if isinstance(value, date):
                        value = value.strftime("%d/%m/%Y")
                    
                    # Establecer valor en todas las celdas del mapeo
                    for cell_ref in cell_refs:
                        self._set_cell_value(worksheet, cell_ref, value)
            
            # Paso 5: Añadir perforaciones si existen
            if perforaciones:
                self._add_perforaciones(worksheet, perforaciones, categoria)
            
            # Paso 6: Guardar archivo
            workbook.save(work_file)
            workbook.close()
            
            logger.info(f"Excel generado exitosamente: {work_file}")
            return work_file
            
        except Exception as e:
            logger.error(f"Error al generar Excel: {str(e)}")
            raise
    
    def verify_templates(self) -> dict:
        """Verifica que todas las plantillas existan"""
        templates_status = {}
        
        for categoria in ["1", "2", "3"]:
            try:
                path = self._get_template_path(categoria)
                templates_status[f"Categoria{categoria}"] = {
                    "exists": True,
                    "path": str(path),
                }
            except FileNotFoundError:
                templates_status[f"Categoria{categoria}"] = {
                    "exists": False,
                    "path": str(self.templates_dir / f"plantilla_categoria_{categoria}.xlsx"),
                }
        
        return templates_status


# Instancia global del servicio
excel_service = ExcelService()
