"""Document orchestration service for the Excel templates."""

import logging
from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Optional
from copy import copy
import re
import shutil
import unicodedata
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from openpyxl import load_workbook
from openpyxl.formula.translate import Translator
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Alignment, PatternFill

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

    def _prepare_profile_file(
        self,
        source_template: Path,
        project_id: str,
        project_value,
        fecha_value,
        fecha_original=None,
        perforaciones: Optional[List[Dict]] = None,
    ) -> Path:
        output_name = f"{project_id}_{source_template.stem}.xlsx"
        output_path = self.excel_service.generated_dir / output_name

        shutil.copy2(source_template, output_path)

        workbook = load_workbook(output_path)
        worksheet = workbook.active
        worksheet["D1"] = project_value

        def _truncate_depth(value) -> Optional[int]:
            if value in (None, ""):
                return None
            text = str(value).strip().replace(",", ".")
            try:
                return max(1, int(float(text)))
            except Exception:
                return None

        def _profile_block_ranges(ws, start_row: int = 5):
            ranges = []
            handled_rows = set()
            for row_number in range(start_row, ws.max_row + 1):
                if row_number in handled_rows:
                    continue

                d_cell = ws[f"D{row_number}"]
                if isinstance(d_cell, MergedCell):
                    continue

                containing_merges = [
                    merged_range
                    for merged_range in ws.merged_cells.ranges
                    if merged_range.min_row <= row_number <= merged_range.max_row
                    and merged_range.min_col <= 4 <= merged_range.max_col
                ]

                if not containing_merges and d_cell.value in (None, ""):
                    continue

                row_end = max((merged_range.max_row for merged_range in containing_merges), default=row_number)
                ranges.append((row_number, row_end))
                handled_rows.update(range(row_number, row_end + 1))

            return ranges

        def _clear_cell_if_writable(ws, cell_ref: str):
            cell = ws[cell_ref]
            if isinstance(cell, MergedCell):
                return
            cell.value = None
            cell.fill = PatternFill(fill_type=None)

        def _apply_profile_j_formulas(ws):
            for start_row, end_row in _profile_block_ranges(ws):
                span_rows = end_row - start_row + 1
                if span_rows == 1:
                    formula = f"=I{start_row}"
                else:
                    i_terms = "+".join([f"I{row_number}" for row_number in range(start_row, end_row + 1)])
                    formula = f"=({i_terms})/{span_rows}"
                ws[f"J{start_row}"] = formula
                ws[f"D{start_row}"].number_format = "0.00"


        profile_name = source_template.name.upper()
        if any(tag in profile_name for tag in ("6M", "15M", "25M")):
            max_depth_row = 0
            for row_number in range(5, worksheet.max_row + 1):
                c_value = worksheet[f"C{row_number}"].value
                if c_value in (None, ""):
                    continue
                try:
                    float(str(c_value).replace(",", "."))
                    max_depth_row = row_number
                except Exception:
                    continue

            layers = list(perforaciones or [])
            mirror_columns = ["J", "K", "L", "M"]
            mirror_sources = [5, 6]
            mirror_template_values = {
                source_row: {
                    column: worksheet[f"{column}{source_row}"].value for column in mirror_columns
                }
                for source_row in mirror_sources
            }

            def _copy_formula_or_value(source_cell_ref: str, target_cell_ref: str):
                source_value = mirror_template_values[int("".join(ch for ch in source_cell_ref if ch.isdigit()))][
                    "".join(ch for ch in source_cell_ref if ch.isalpha())
                ]
                if isinstance(source_value, str) and source_value.startswith("="):
                    try:
                        return Translator(source_value, origin=source_cell_ref).translate_formula(target_cell_ref)
                    except Exception:
                        return source_value
                return source_value

            def _depth_floor(value) -> Optional[int]:
                parsed_depth = _truncate_depth(value)
                return parsed_depth if parsed_depth is not None else None

            depth_rows = list(range(5, max_depth_row + 1))
            if layers:
                cleaned_layers = []
                previous_floor = 0
                for index, layer in enumerate(layers):
                    depth_floor = _depth_floor(layer.get("profundidad_z"))
                    if depth_floor is None:
                        depth_floor = previous_floor + 1
                    if depth_floor <= previous_floor:
                        depth_floor = previous_floor + 1

                    cleaned_layers.append((layer, depth_floor))
                    previous_floor = depth_floor

                total_visible_rows = len(depth_rows)
                spans: List[int] = []
                previous_floor = 0
                for index, (_, depth_floor) in enumerate(cleaned_layers):
                    span_rows = max(1, depth_floor - previous_floor)
                    spans.append(span_rows)
                    previous_floor = depth_floor

                if spans and sum(spans) < total_visible_rows:
                    spans[-1] += total_visible_rows - sum(spans)
                elif spans and sum(spans) > total_visible_rows:
                    overflow = sum(spans) - total_visible_rows
                    spans[-1] = max(1, spans[-1] - overflow)

                # Rebuild only the layer area so the number of visible layers matches the input.
                for merged_range in list(worksheet.merged_cells.ranges):
                    if merged_range.min_row > max_depth_row or merged_range.max_row < 5:
                        continue
                    if (
                        merged_range.min_col in {2, 4, 10, 11, 12, 13}
                        or merged_range.max_col in {2, 4, 10, 11, 12, 13}
                    ):
                        worksheet.unmerge_cells(str(merged_range))

                for row_number in depth_rows:
                    worksheet[f"B{row_number}"] = None
                    worksheet[f"D{row_number}"] = None
                    worksheet[f"B{row_number}"].fill = PatternFill(fill_type=None)
                    worksheet[f"D{row_number}"].fill = PatternFill(fill_type=None)

                for row_number in depth_rows:
                    for column in mirror_columns:
                        worksheet[f"{column}{row_number}"].fill = PatternFill(fill_type=None)

                current_row = depth_rows[0]
                for index, ((layer, depth_floor), span_rows) in enumerate(zip(cleaned_layers, spans)):
                    row_end = min(max_depth_row, current_row + span_rows - 1)
                    if index == len(spans) - 1:
                        row_end = max_depth_row

                    soil_name = self.excel_service._clean_soil_text(
                        layer.get("descripcion_suelo"),
                        layer.get("color_predominante"),
                    )
                    if not soil_name:
                        soil_name = self.excel_service._clean_soil_text(
                            layer.get("tipo_suelo_principal"),
                            layer.get("color_predominante"),
                        )

                    fill, font_color = self.excel_service._soil_style_from_color(layer.get("color_predominante"))

                    b_anchor = worksheet[f"B{current_row}"]
                    d_anchor = worksheet[f"D{current_row}"]

                    b_anchor.value = soil_name
                    b_anchor.fill = fill
                    b_anchor.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                    b_font = copy(b_anchor.font)
                    b_font.color = font_color
                    b_anchor.font = b_font

                    d_anchor.value = float(span_rows)
                    d_anchor.number_format = "0.00"
                    d_anchor.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

                    source_row = mirror_sources[0] if index == 0 else mirror_sources[-1]
                    for column in mirror_columns:
                        target_anchor = worksheet[f"{column}{current_row}"]
                        if column == 'J':
                            i_terms = "+".join([f"I{row_number}" for row_number in range(current_row, row_end + 1)])
                            target_anchor.value = f"=({i_terms})/{span_rows}"
                        else:
                            target_anchor.value = _copy_formula_or_value(f"{column}{source_row}", f"{column}{current_row}")
                        target_anchor.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

                    if row_end > current_row:
                        worksheet.merge_cells(start_row=current_row, start_column=2, end_row=row_end, end_column=2)
                        worksheet.merge_cells(start_row=current_row, start_column=4, end_row=row_end, end_column=4)
                        for column_letter in mirror_columns:
                            column_index = ord(column_letter) - ord("A") + 1
                            worksheet.merge_cells(start_row=current_row, start_column=column_index, end_row=row_end, end_column=column_index)

                    current_row = row_end + 1
                    if current_row > max_depth_row:
                        break

                for row_number in range(current_row, max_depth_row + 1):
                    _clear_cell_if_writable(worksheet, f"B{row_number}")
                    _clear_cell_if_writable(worksheet, f"D{row_number}")

                # If there are more capas than visible depth rows, collapse the extras into the last layer.
                if "15M" in profile_name or "25M" in profile_name:
                    worksheet["M1"] = "FECHA"
                    worksheet["N1"] = fecha_value
                else:
                    worksheet["M1"] = fecha_value
                    worksheet["N1"] = None
            else:
                for row_number in depth_rows:
                    _clear_cell_if_writable(worksheet, f"B{row_number}")
                    _clear_cell_if_writable(worksheet, f"D{row_number}")
                if "15M" in profile_name or "25M" in profile_name:
                    worksheet["M1"] = "FECHA"
                    worksheet["N1"] = fecha_value
                else:
                    worksheet["M1"] = fecha_value
                    worksheet["N1"] = None
        else:
            worksheet["N1"] = fecha_value

        if any(tag in profile_name for tag in ("6M", "15M", "25M")):
            _apply_profile_j_formulas(worksheet)
        workbook.save(output_path)
        workbook.close()

        return output_path
    
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
                batch_templates = [capacity_template_id, correlation_template_id, *laboratorio_template_ids, '9']
                if nPisos <= 3:
                    perfil_template_name = 'PERFIL DEL SUELO 6M.xlsx'
                elif nPisos <= 10:
                    perfil_template_name = 'PERFIL DEL SUELO 15M.xlsx'
                else:
                    perfil_template_name = 'PERFIL DEL SUELO 25M.xlsx'
                perfil_template_path = self.excel_service.templates_dir / perfil_template_name

                client_slug = self._slugify_filename(str(cliente or '').strip(), 'cliente')
                project_slug = self._slugify_filename(proyecto_upper, 'proyecto')
                zip_base_name = f"{client_slug} - {project_slug}.zip"
                zip_path = self.excel_service.generated_dir / zip_base_name

                output_files = []
                perfil_added = False
                perfil_error = None
                perfil_generated_file = None
                asentamientos_template_ids = ['10', '11']
                batch_templates_with_asentamientos = [*batch_templates, *asentamientos_template_ids]

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

                    asentamientos_template_names = {
                        '10': 'ASENTAMIENTOS ZAPATAS 300.xlsx',
                        '11': 'ASENTAMIENTOS ZAPATAS 800.xlsx',
                    }
                    for current_template in asentamientos_template_ids:
                        generated_file = self.excel_service.generate_excel(
                            template_id=current_template,
                            project_id=project_id,
                            data=excel_data,
                            perforaciones=default_perforaciones,
                            parametros=parametros or [],
                        )
                        output_files.append(generated_file)
                        zip_file.write(generated_file, arcname=asentamientos_template_names[current_template])

                    if perfil_template_path.exists():
                        try:
                            perfil_generated_file = self._prepare_profile_file(
                                source_template=perfil_template_path,
                                project_id=project_id,
                                project_value=proyecto_upper,
                                fecha_value=excel_data.get("fecha_registro"),
                                fecha_original=excel_data.get("fecha_registro_original"),
                                perforaciones=default_perforaciones,
                            )
                            output_files.append(perfil_generated_file)
                            zip_file.write(perfil_generated_file, arcname=perfil_template_name)
                            perfil_added = True
                        except PermissionError:
                            perfil_error = f"No se pudo agregar el perfil de suelo requerido ({perfil_template_name}) porque está abierto en Excel: {perfil_template_path}"
                            logger.warning(perfil_error)
                        except Exception:
                            perfil_error = f"No se pudo agregar el perfil de suelo requerido ({perfil_template_name}) al ZIP"
                            logger.warning(perfil_error, exc_info=True)
                    else:
                        perfil_error = f"No se encontró la plantilla de perfil de suelo requerida: {perfil_template_path}"
                        logger.warning(perfil_error)

                if not perfil_added:
                    raise RuntimeError(perfil_error or f"No se pudo incluir el perfil de suelo requerido: {perfil_template_name}")

                return {
                    "success": True,
                    "message": "Documentos generados exitosamente en paquete ZIP",
                    "project_id": project_id,
                    "files": [str(file_path) for file_path in output_files] + [str(zip_path)],
                    "download_url": f"/api/download/{zip_path.name}",
                    "timestamp": timestamp,
                    "template_id": ",".join(batch_templates_with_asentamientos),
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
