"""Excel service for the two geotechnical templates."""

from __future__ import annotations

import logging
import random
import shutil
import unicodedata
from datetime import date
from copy import copy
from pathlib import Path
from typing import List, Optional
from tempfile import NamedTemporaryFile
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from openpyxl.utils.cell import column_index_from_string, coordinate_from_string
from openpyxl.styles import Alignment, Font, PatternFill
 
import openpyxl
from openpyxl import load_workbook

from app.core.config import settings
from app.utils.field_mapping import (
    get_field_mapping,
    get_parametros_mapping,
    get_perforacion_mapping,
)

logger = logging.getLogger(__name__)

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NS = {"main": MAIN_NS, "rel": REL_NS}


class ExcelService:
    """Service responsible for copying and filling Excel templates."""

    def __init__(self):
        self.templates_dir = settings.EXCEL_TEMPLATES_DIR
        self.generated_dir = settings.GENERATED_DIR

    def _normalize(self, value: str) -> str:
        return unicodedata.normalize("NFD", value).encode("ascii", "ignore").decode("ascii").lower()

    def _get_template_path(self, template_id: str) -> Path:
        template_filename = settings.TEMPLATES_CONFIG.get(str(template_id))
        if not template_filename:
            raise FileNotFoundError(f"Plantilla no configurada para template_id={template_id}")

        template_path = self.templates_dir / template_filename
        if not template_path.exists():
            raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")

        return template_path

    def _copy_template(self, template_id: str, project_id: str) -> Path:
        template_path = self._get_template_path(template_id)
        output_filename = f"{project_id}_template_{template_id}.xlsx"
        output_path = self.generated_dir / output_filename
        shutil.copy2(template_path, output_path)
        logger.info("Plantilla copiada: %s -> %s", template_path, output_path)
        return output_path

    def _set_cell_value(self, worksheet, cell_ref: str, value):
        if ":" in cell_ref:
            cell_ref = cell_ref.split(":")[0]

        cell = worksheet[cell_ref]
        if cell.__class__.__name__ == "MergedCell":
            column_letter, row_number = coordinate_from_string(cell_ref)
            column_number = column_index_from_string(column_letter)
            for merged_range in worksheet.merged_cells.ranges:
                if merged_range.min_row <= row_number <= merged_range.max_row and merged_range.min_col <= column_number <= merged_range.max_col:
                    worksheet[merged_range.start_cell.coordinate] = value
                    return

        worksheet[cell_ref] = value

    def _get_sheet(self, workbook, target_name: str):
        normalized_target = self._normalize(target_name)
        for sheet_name in workbook.sheetnames:
            if self._normalize(sheet_name) == normalized_target:
                return workbook[sheet_name]
        return workbook.active

    def _resolve_sheet_targets(self, workbook_path: Path) -> dict:
        with ZipFile(workbook_path, "r") as workbook_zip:
            workbook_xml = ET.fromstring(workbook_zip.read("xl/workbook.xml"))
            rels_xml = ET.fromstring(workbook_zip.read("xl/_rels/workbook.xml.rels"))

        rel_map = {rel.get("Id"): rel.get("Target") for rel in rels_xml}
        sheet_targets = {}

        for sheet in workbook_xml.findall("main:sheets/main:sheet", NS):
            sheet_name = sheet.get("name", "")
            rel_id = sheet.get(f"{{{REL_NS}}}id")
            target = rel_map.get(rel_id)
            if not target:
                continue

            if target.startswith("/"):
                target = target.lstrip("/")
            if not target.startswith("xl/"):
                target = f"xl/{target}"

            sheet_targets[self._normalize(sheet_name)] = target

        return sheet_targets

    def _cell_sort_key(self, cell_ref: str):
        letters = ""
        digits = ""
        for character in cell_ref:
            if character.isdigit():
                digits += character
            else:
                letters += character
        return int(digits or 0), column_index_from_string(letters or "A")

    def _soil_style_from_color(self, color_name: Optional[str]):
        color_map = {
            "verde": "92D050",
            "verde claro": "C6E0B4",
            "beige": "F5F0D7",
            "café": "8B5A2B",
            "cafe": "8B5A2B",
            "amarillo": "FFD966",
            "rojizo": "C0504D",
            "blanco": "FFFFFF",
            "gris claro": "D9D9D9",
            "naranja": "F4B183",
        }
        normalized = self._normalize(color_name or "")
        fill_hex = color_map.get(normalized, "F4B183")

        def is_dark(hex_color: str) -> bool:
            red = int(hex_color[0:2], 16)
            green = int(hex_color[2:4], 16)
            blue = int(hex_color[4:6], 16)
            return (red * 299 + green * 587 + blue * 114) / 1000 < 140

        font_color = "FFFFFF" if is_dark(fill_hex) else "1F2937"
        return PatternFill(fill_type="solid", fgColor=fill_hex), font_color

    def _parse_depth_value(self, value) -> Optional[float]:
        try:
            if value in (None, ""):
                return None
            parsed = float(str(value).replace(",", ".").strip())
            return parsed if parsed > 0 else None
        except Exception:
            return None

    def _clean_soil_text(self, value: Optional[str], color_name: Optional[str] = None) -> str:
        text = str(value or "").strip()
        if not text:
            return ""

        normalized = self._normalize(text)
        for separator in (" de color ", " color "):
            token = separator.strip()
            index = normalized.find(token)
            if index != -1:
                text = text[:index].strip()
                normalized = self._normalize(text)

        if color_name:
            normalized_color = self._normalize(color_name)
            if normalized_color:
                index = normalized.find(f" color {normalized_color}")
                if index != -1:
                    text = text[:index].strip()

        text = text.replace("de color", "").replace(" color ", " ")
        return " ".join(text.split())

    def _build_soil_segments(self, worksheet, layers: List[dict], start_row: int, end_row: int) -> List[tuple]:
        valid_layers = [layer for layer in layers if any((layer.get(key) for key in ("descripcion_suelo", "tipo_suelo_principal", "color_predominante")))]
        if not valid_layers:
            return []

        depth_rows: List[tuple[int, float]] = []
        for row_number in range(start_row, end_row + 1):
            marker = self._parse_depth_value(worksheet[f"A{row_number}"].value)
            if marker is not None:
                depth_rows.append((row_number, marker))

        if not depth_rows:
            visible_rows = max(1, end_row - start_row + 1)
            depths: List[float] = []
            for index, layer in enumerate(valid_layers):
                raw_depth = layer.get("profundidad_z")
                try:
                    depth = float(raw_depth)
                except Exception:
                    depth = float(index + 1)
                if depth <= 0:
                    depth = float(index + 1)
                depths.append(depth)

            if any(depths[index] <= depths[index - 1] for index in range(1, len(depths))):
                depths = [float(index + 1) for index in range(len(valid_layers))]

            total_depth = depths[-1] if depths[-1] > 0 else float(len(valid_layers))
            if total_depth <= 0:
                total_depth = float(len(valid_layers))

            raw_spans: List[int] = []
            previous_depth = 0.0
            for index, depth in enumerate(depths):
                delta = max(0.0, depth - previous_depth)
                if index == len(depths) - 1 and delta <= 0:
                    delta = total_depth - previous_depth
                span_rows = int(round((delta / total_depth) * visible_rows)) if total_depth else 1
                raw_spans.append(max(1, span_rows))
                previous_depth = depth

            difference = visible_rows - sum(raw_spans)
            if raw_spans:
                raw_spans[-1] = max(1, raw_spans[-1] + difference)
                while sum(raw_spans) > visible_rows and raw_spans[-1] > 1:
                    raw_spans[-1] -= 1

            segments = []
            current_row = start_row
            for index, span_rows in enumerate(raw_spans):
                row_end = min(end_row, current_row + span_rows - 1)
                if index == len(raw_spans) - 1:
                    row_end = end_row
                segments.append((current_row, row_end, valid_layers[index]))
                current_row = row_end + 1
                if current_row > end_row:
                    break

            return segments

        # If template provides explicit depth markers but user provided fewer layers,
        # repeat the last provided layer until there are as many layers as depth markers.
        if depth_rows and len(valid_layers) < len(depth_rows):
            last = valid_layers[-1]
            while len(valid_layers) < len(depth_rows):
                # append a shallow copy so modifications don't affect original
                valid_layers.append(dict(last))

        depths: List[float] = []
        for index, layer in enumerate(valid_layers):
            raw_depth = layer.get("profundidad_z")
            try:
                depth = float(raw_depth)
            except Exception:
                depth = float(index + 1)
            if depth <= 0:
                depth = float(index + 1)
            depths.append(depth)

        if any(depths[index] <= depths[index - 1] for index in range(1, len(depths))):
            depths = [float(index + 1) for index in range(len(valid_layers))]

        segments = []
        current_row = start_row
        for index, depth in enumerate(depths):
            row_end = end_row
            for row_number, marker in depth_rows:
                if marker >= depth:
                    row_end = row_number
                    break
            segments.append((current_row, row_end, valid_layers[index]))
            current_row = row_end + 1
            if current_row > end_row:
                break

        return segments

    def _clear_cell_children(self, cell):
        for child in list(cell):
            cell.remove(child)

    def _set_xml_cell_value(self, cell, value):
        self._clear_cell_children(cell)

        if value is None or value == "":
            return

        if isinstance(value, bool):
            cell.set("t", "b")
            v_element = ET.SubElement(cell, f"{{{MAIN_NS}}}v")
            v_element.text = "1" if value else "0"
            return

        if isinstance(value, (int, float)):
            cell.set("t", "n")
            v_element = ET.SubElement(cell, f"{{{MAIN_NS}}}v")
            v_element.text = str(value)
            return

        cell.set("t", "inlineStr")
        inline_string = ET.SubElement(cell, f"{{{MAIN_NS}}}is")
        text_element = ET.SubElement(inline_string, f"{{{MAIN_NS}}}t")
        text_value = str(value)
        if text_value != text_value.strip():
            text_element.set(f"{{{XML_NS}}}space", "preserve")
        text_element.text = text_value

    def _ensure_row(self, sheet_data, row_number: int):
        rows = sheet_data.findall(f"{{{MAIN_NS}}}row")
        for row in rows:
            if int(row.get("r", "0")) == row_number:
                return row

        new_row = ET.Element(f"{{{MAIN_NS}}}row", {"r": str(row_number)})
        insert_at = len(rows)
        for index, row in enumerate(rows):
            if int(row.get("r", "0")) > row_number:
                insert_at = index
                break
        sheet_data.insert(insert_at, new_row)
        return new_row

    def _ensure_cell(self, row, cell_ref: str):
        cells = row.findall(f"{{{MAIN_NS}}}c")
        for cell in cells:
            if cell.get("r") == cell_ref:
                return cell

        new_cell = ET.Element(f"{{{MAIN_NS}}}c", {"r": cell_ref})
        insert_at = len(cells)
        target_sort_key = self._cell_sort_key(cell_ref)
        for index, cell in enumerate(cells):
            if self._cell_sort_key(cell.get("r", "A1")) > target_sort_key:
                insert_at = index
                break
        row.insert(insert_at, new_cell)
        return new_cell

    def _update_sheet_xml(self, sheet_xml: bytes, cell_updates: dict) -> bytes:
        root = ET.fromstring(sheet_xml)
        sheet_data = root.find(f"{{{MAIN_NS}}}sheetData")
        if sheet_data is None:
            return sheet_xml

        for cell_ref, value in cell_updates.items():
            digits = "".join(ch for ch in cell_ref if ch.isdigit())
            row_number = int(digits or "0")
            row = self._ensure_row(sheet_data, row_number)
            cell = self._ensure_cell(row, cell_ref)
            self._set_xml_cell_value(cell, value)

        

        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def _write_workbook_preserving_parts(self, workbook_path: Path, sheet_updates: dict) -> None:
        with ZipFile(workbook_path, "r") as source_zip:
            source_entries = [(info, source_zip.read(info.filename)) for info in source_zip.infolist()]

        with NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            temp_path = Path(temp_file.name)

        try:
            with ZipFile(temp_path, "w", compression=ZIP_DEFLATED) as target_zip:
                for info, data in source_entries:
                    # sanitize workbook.xml to remove AlternateContent blocks that reference absolute paths
                    if info.filename == 'xl/workbook.xml':
                        try:
                            wb_root = ET.fromstring(data)
                            mc_ns = 'http://schemas.openxmlformats.org/markup-compatibility/2006'
                            # remove all mc:AlternateContent elements
                            for ac in wb_root.findall('.//{'+mc_ns+'}AlternateContent'):
                                parent = wb_root
                                # find parent by searching for the element and removing it from its parent
                                # since ElementTree doesn't provide parent pointers, rebuild without AlternateContent
                            # Safer approach: serialize to string and remove AlternateContent segments by tag
                            s = ET.tostring(wb_root, encoding='utf-8')
                            try:
                                s_dec = s.decode('utf-8')
                                # naive removal: remove '<mc:AlternateContent' blocks
                                import re
                                s_clean = re.sub(r'<\/?(?:\w+:)?AlternateContent[^>]*>(?:.|\n|\r)*?<\/?(?:\w+:)?AlternateContent>', '', s_dec)
                                data = s_clean.encode('utf-8')
                            except Exception:
                                pass
                        except Exception:
                            # if parsing fails, fall back to original data
                            data = data
                    if info.filename in sheet_updates:
                        replacement = sheet_updates[info.filename]
                        if isinstance(replacement, (bytes, bytearray)):
                            data = replacement
                        else:
                            # assume mapping of cell updates
                            data = self._update_sheet_xml(data, replacement)
                    target_zip.writestr(info, data)
            # replace original workbook atomically when possible
            try:
                if workbook_path.exists():
                    workbook_path.unlink()
                shutil.move(str(temp_path), str(workbook_path))
            except Exception:
                # best-effort move; re-raise to let caller handle
                raise
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def _extract_first_image_anchor(self, template_path: Path) -> Optional[tuple]:
        return None
        

    def _fill_general_fields(self, worksheet, template_id: str, data: dict):
        field_mapping = get_field_mapping(template_id)
        for field_name, cell_refs in field_mapping.items():
            value = data.get(field_name)
            if value is None:
                continue

            if isinstance(value, date):
                value = value.strftime("%d/%m/%Y")

            for cell_ref in cell_refs:
                self._set_cell_value(worksheet, cell_ref, value)

    def _format_client(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        try:
            return str(value).strip().upper()
        except Exception:
            return str(value)

    def _fill_rows(self, worksheet, mapping: dict, rows: List[dict], seed: str = ""):
        if not rows:
            return

        start_row = mapping["tabla_inicio_row"]
        allowed_columns = mapping["allowed_columns"]
        rng = random.SystemRandom()
        reduce_next = bool(rng.getrandbits(1))

        for index, row_data in enumerate(rows):
            row_number = start_row + index
            for field_name, column_letter in allowed_columns.items():
                if field_name == "profundidad_z":
                    continue

                value = row_data.get(field_name, "")

                if field_name == "n_campo_spt" and 10 <= row_number <= 16 and isinstance(value, int):
                    value = max(0, value - 1) if reduce_next else value
                    reduce_next = not reduce_next

                self._set_cell_value(worksheet, f"{column_letter}{row_number}", value)

    def generate_excel(
        self,
        template_id: str,
        project_id: str,
        data: dict,
        perforaciones: Optional[List[dict]] = None,
        parametros: Optional[List[dict]] = None,
    ) -> Path:
        work_file = self._copy_template(template_id, project_id)

        if str(template_id) == '8':
            try:
                wb_tmp = load_workbook(work_file)
                target_sheet = self._get_sheet(wb_tmp, 'MÉTODO TERZAGHI')

                project_value = data.get('proyecto_ubicacion')
                client_value = self._format_client(data.get('cliente'))
                fecha_value = data.get('fecha_registro')

                # Construct header describing the structure levels based on 'pisos'
                pisos_value = data.get('pisos')
                try:
                    pisos_int = int(pisos_value or 0)
                except Exception:
                    pisos_int = 0
                if pisos_int == 1:
                    estructura_text = 'ESTRUCTURA DE CONSTRUCCIÓN DE 1 NIVEL'
                elif pisos_int > 1:
                    estructura_text = f'ESTRUCTURA DE CONSTRUCCIÓN DE {pisos_int} NIVELES'
                else:
                    estructura_text = 'ESTRUCTURA DE CONSTRUCCIÓN'
                self._set_cell_value(target_sheet, 'E1', estructura_text)
                self._set_cell_value(target_sheet, 'E2', project_value)
                self._set_cell_value(target_sheet, 'E3', client_value)
                self._set_cell_value(target_sheet, 'E5', fecha_value)

                # Keep the worksheet's existing formula structure; only refresh the
                # standard project metadata so it reflects the current frontend.
                wb_tmp.save(work_file)
                wb_tmp.close()
            finally:
                try:
                    self._remove_calcchain(work_file)
                except Exception:
                    logger.debug("No se pudo eliminar calcChain del libro generado", exc_info=True)

            logger.info("Excel generado exitosamente: %s", work_file)
            return work_file

        laboratorio_template_ids = {'4', '5', '6', '7'}
        if str(template_id) in laboratorio_template_ids:
            try:
                wb_tmp = load_workbook(work_file)
                target_sheet = None
                for sheet_name in wb_tmp.sheetnames:
                    if self._normalize(sheet_name) == self._normalize('Clasificacion'):
                        target_sheet = wb_tmp[sheet_name]
                        break
                if target_sheet is None:
                    target_sheet = wb_tmp[wb_tmp.sheetnames[0]]

                project_value = data.get('proyecto_ubicacion')
                cliente_value = self._format_client(data.get('cliente'))
                fecha_original_value = data.get('fecha_registro_original', data.get('fecha_registro'))
                fecha_plus_20_value = data.get('fecha_registro')
                self._set_cell_value(target_sheet, 'H2', project_value)
                self._set_cell_value(target_sheet, 'Q4', fecha_original_value)
                self._set_cell_value(target_sheet, 'L2', fecha_plus_20_value)
                self._set_cell_value(target_sheet, 'E5', cliente_value)

                random_values = random.sample(range(10, 100), 3)
                for cell_ref, value in zip(('K13', 'L13', 'M13'), random_values):
                    self._set_cell_value(target_sheet, cell_ref, value)

                wb_tmp.save(work_file)
                wb_tmp.close()
            finally:
                try:
                    self._remove_calcchain(work_file)
                except Exception:
                    logger.debug("No se pudo eliminar calcChain del libro generado", exc_info=True)

            logger.info("Excel generado exitosamente: %s", work_file)
            return work_file

        sheet_targets = self._resolve_sheet_targets(work_file)
        sheet_updates = {}

        primary_updates = {}
        field_mapping = get_field_mapping(template_id)
        for field_name, cell_refs in field_mapping.items():
            value = data.get(field_name)
            if value is None:
                continue

            if isinstance(value, date):
                value = value.strftime("%d/%m/%Y")

            for cell_ref in cell_refs:
                primary_updates[cell_ref] = value

        perforacion_mapping = get_perforacion_mapping(template_id)
        start_row = perforacion_mapping["tabla_inicio_row"]
        allowed_columns = perforacion_mapping["allowed_columns"]
        if str(template_id) == "1":
            f_end = 16
        elif str(template_id) == "2":
            f_end = 25
        elif str(template_id) == "3":
            f_end = 35
        else:
            f_end = start_row + max(0, len(perforaciones or [])) - 1

        rng = random.SystemRandom()
        reduce_next = bool(rng.getrandbits(1))

        for index, row_data in enumerate(perforaciones or []):
            row_number = start_row + index
            for field_name, column_letter in allowed_columns.items():
                if field_name == "profundidad_z":
                    continue
                if field_name == "descripcion_suelo":
                    continue

                value = row_data.get(field_name, "")
                if field_name == "n_campo_spt" and 10 <= row_number <= 16 and isinstance(value, int):
                    value = max(0, value - 1) if reduce_next else value
                    reduce_next = not reduce_next

                primary_updates[f"{column_letter}{row_number}"] = value

        # Gamma column B starts at 15 and increments by layer across the visible rows.
        # This keeps the gamma values tied to the discovered layers.
        layer_count = len(perforaciones or [])
        if layer_count > 0:
            for index in range(layer_count):
                primary_updates[f"B{start_row + index}"] = 15 + index
            last_gamma = 15 + max(0, layer_count - 1)
            for row_number in range(start_row + layer_count, f_end + 1):
                primary_updates[f"B{row_number}"] = last_gamma
        else:
            for row_number in range(start_row, f_end + 1):
                primary_updates[f"B{row_number}"] = None

        # If the soil description column is empty, mirror the same-row L cell.
        for row_number in range(start_row, f_end + 1):
            p_cell = f"P{row_number}"
            if primary_updates.get(p_cell) in (None, ""):
                primary_updates[p_cell] = f"=L{row_number}"

        # Enforce specific SPT values per plantilla
        if str(template_id) == "1":
            spt_values = [7, 8, 15, 19, 23, 26, 29]
            spt_start = 10
            for i, v in enumerate(spt_values):
                primary_updates[f"F{spt_start + i}"] = v
        elif str(template_id) == "3":
            # Secuencia completa proporcionada por el usuario para F10:F35 (26 valores)
            spt_values_3 = [
                13, 17, 28, 35, 40, 46, 45, 49, 50, 53, 55, 58, 60, 63,
                65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65,
            ]
            spt_start = 10
            for i, v in enumerate(spt_values_3):
                primary_updates[f"F{spt_start + i}"] = v
        elif str(template_id) == "2":
            # Valores proporcionados por el usuario para plantilla 2 F10:F25
            spt_values_2 = [
                15, 20, 22, 29, 35, 38, 42, 45, 48, 51, 54, 57, 59, 62, 65, 68,
            ]
            spt_start = 10
            for i, v in enumerate(spt_values_2):
                primary_updates[f"F{spt_start + i}"] = v

        # Convert the numeric SPT values in column F into ranges like "6-7", "7-8",
        # using the final value that will appear in column F. Apply across the full
        # target range for each plantilla so the visible SPT block shows ranges.
        # Decide per-copy whether to show the lower or upper value.
        # Implement alternating behavior across generated files using a toggle file
        # stored under the generated directory so successive calls flip choice.
        toggle_file = Path(self.generated_dir) / '.n_campo_toggle'
        try:
            if not toggle_file.exists():
                toggle_file.write_text('0')
            counter = int(toggle_file.read_text() or '0')
        except Exception:
            counter = 0

        # even -> show lower (e.g., 6), odd -> show upper (e.g., 7)
        use_lower = (counter % 2 == 0)

        # After reading, increment and persist for next generation
        try:
            toggle_file.write_text(str(counter + 1))
        except Exception:
            pass

        for row_num in range(start_row, f_end + 1):
            f_cell = f"F{row_num}"
            raw = primary_updates.get(f_cell)
            try:
                v = int(float(raw))
            except Exception:
                continue
            lower = max(0, v - 1)
            upper = v
            primary_updates[f_cell] = str(lower) if use_lower else str(upper)
        if primary_updates:
            primary_sheet = sheet_targets.get(self._normalize("P3"))
            if primary_sheet:
                sheet_updates[primary_sheet] = primary_updates

        parametros_updates = {}
        parametros_mapping = get_parametros_mapping(template_id)
        for index, row_data in enumerate(parametros or []):
            row_number = parametros_mapping["tabla_inicio_row"] + index
            for field_name, column_letter in parametros_mapping["allowed_columns"].items():
                parametros_updates[f"{column_letter}{row_number}"] = row_data.get(field_name, "")

        if parametros_updates:
            parametros_sheet = sheet_targets.get(self._normalize("Parametros"))
            if parametros_sheet:
                sheet_updates[parametros_sheet] = parametros_updates

        if sheet_updates:
            # Simpler approach: load the copied template with openpyxl, apply updates and save.
            try:
                wb_tmp = load_workbook(work_file)
                # reverse map from target path to normalized sheet name
                target_to_sheetname = {v.lstrip('/'): k for k, v in sheet_targets.items()}
                for target_path, updates in sheet_updates.items():
                    normalized_target = target_path.lstrip('/')
                    norm_sheet = target_to_sheetname.get(normalized_target)
                    if not norm_sheet:
                        # try matching without xl/ prefix
                        norm_sheet = target_to_sheetname.get(normalized_target.replace('xl/',''))
                    if not norm_sheet:
                        continue
                    # find actual sheet by normalized name
                    sheet_obj = None
                    for name in wb_tmp.sheetnames:
                        if self._normalize(name) == norm_sheet:
                            sheet_obj = wb_tmp[name]
                            break
                    if not sheet_obj:
                        continue
                    for cell_ref, value in updates.items():
                        try:
                            # write into merged anchors if necessary
                            if ':' in cell_ref:
                                cell_ref = cell_ref.split(':')[0]
                            cell = sheet_obj[cell_ref]
                            if cell.__class__.__name__ == 'MergedCell':
                                for merged_range in sheet_obj.merged_cells.ranges:
                                    if cell_ref in merged_range:
                                        sheet_obj[merged_range.start_cell.coordinate] = value
                                        break
                            else:
                                sheet_obj[cell_ref] = value
                        except Exception:
                            continue

                    def build_soil_text(layer: dict) -> str:
                        descripcion = self._clean_soil_text(layer.get('descripcion_suelo'), layer.get('color_predominante'))
                        if descripcion:
                            return descripcion
                        tipo = self._clean_soil_text(layer.get('tipo_suelo_principal'), layer.get('color_predominante'))
                        return tipo

                    q_segments = self._build_soil_segments(sheet_obj, list(perforaciones or []), start_row, f_end)

                    # Coalesce adjacent segments that render the same soil text so they
                    # appear as a single merged block (user requested centrar y combinarlas)
                    def _segment_text(seg):
                        return build_soil_text(seg[2])

                    coalesced = []
                    for seg in q_segments:
                        if not coalesced:
                            coalesced.append(list(seg))
                            continue
                        prev = coalesced[-1]
                        if _segment_text(prev) == _segment_text(seg) and seg[0] == prev[1] + 1:
                            # extend previous segment
                            prev[1] = seg[1]
                        else:
                            coalesced.append(list(seg))

                    # normalize back to tuples
                    q_segments = [(s[0], s[1], s[2]) for s in coalesced]

                    for merged_range in list(sheet_obj.merged_cells.ranges):
                        if merged_range.min_col <= 17 <= merged_range.max_col:
                            if merged_range.max_row >= start_row and merged_range.min_row <= f_end:
                                start_cell = merged_range.start_cell.coordinate
                                if start_cell.startswith('Q'):
                                    try:
                                        sheet_obj.unmerge_cells(str(merged_range))
                                    except Exception:
                                        pass

                    for row_start, row_end, layer in q_segments:
                        q_range = f"Q{row_start}" if row_start == row_end else f"Q{row_start}:Q{row_end}"
                        if row_start != row_end:
                            try:
                                sheet_obj.merge_cells(q_range)
                            except Exception:
                                pass

                        q_anchor = sheet_obj[f'Q{row_start}']
                        q_anchor.value = build_soil_text(layer)
                        fill, font_color = self._soil_style_from_color(layer.get('color_predominante'))
                        q_anchor.fill = fill
                        q_anchor.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
                        soil_font = copy(q_anchor.font)
                        soil_font.color = font_color
                        q_anchor.font = soil_font

                        if str(template_id) == "1":
                            gamma_value = layer.get('gamma')
                            for row_number in range(row_start, row_end + 1):
                                b_cell = sheet_obj[f'B{row_number}']
                                b_cell.value = gamma_value
                                b_cell.fill = PatternFill(fill_type=None)
                                b_cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

                # Try to attach default template image if present
                try:
                    from openpyxl.drawing.image import Image as XLImage
                    # image located under templates/imagenes/Imagen1.jpg (not under excel/)
                    from app.core.config import settings as _settings
                    img_path = _settings.TEMPLATES_DIR / 'imagenes' / 'Imagen1.jpg'
                    if img_path.exists():
                        # insert image into primary sheet at a fixed anchor cell (A1)
                        primary_sheet_name = None
                        for name in wb_tmp.sheetnames:
                            if self._normalize(name) == self._normalize('P3'):
                                primary_sheet_name = name
                                break
                        if primary_sheet_name:
                            sheet_obj = wb_tmp[primary_sheet_name]
                            # Only add image if sheet has no images to avoid duplicates/overlaps
                            try:
                                existing_images = list(getattr(sheet_obj, '_images', []))
                            except Exception:
                                existing_images = []
                            if not existing_images:
                                img = XLImage(str(img_path))
                                # Positioning: place top-left corner at cell A1
                                sheet_obj.add_image(img, 'A1')
                except Exception:
                    # non-fatal: ignore image insertion errors
                    pass
                # finally save workbook once after updates and optional image insertion
                wb_tmp.save(work_file)
                wb_tmp.close()
            except Exception:
                # fallback: try the previous xml-replacement method
                try:
                    with NamedTemporaryFile(delete=False, suffix='.xlsx') as tf:
                        temp_saved = Path(tf.name)
                    wb_tmp = load_workbook(work_file)
                    wb_tmp.save(temp_saved)
                    wb_tmp.close()
                    with ZipFile(temp_saved, 'r') as tmpz:
                        tmp_names = tmpz.namelist()
                        replacements = {}
                        for target_path in sheet_updates.keys():
                            normalized = target_path.lstrip('/')
                            if normalized in tmp_names:
                                replacements[normalized] = tmpz.read(normalized)
                    if replacements:
                        self._write_workbook_preserving_parts(work_file, replacements)
                finally:
                    try:
                        if temp_saved.exists():
                            temp_saved.unlink()
                    except Exception:
                        pass

        

        # remove calcChain if present to avoid Excel repair dialogs
        try:
            self._remove_calcchain(work_file)
        except Exception:
            logger.debug("No se pudo eliminar calcChain del libro generado", exc_info=True)

        logger.info("Excel generado exitosamente: %s", work_file)
        return work_file

    def _remove_calcchain(self, workbook_path: Path) -> None:
        # safe remove of xl/calcChain.xml, its override and workbook rel
        with ZipFile(workbook_path, 'r') as src:
            entries = {info.filename: src.read(info.filename) for info in src.infolist()}

        changed = False
        if 'xl/calcChain.xml' in entries:
            entries.pop('xl/calcChain.xml', None)
            changed = True

        # remove override from [Content_Types].xml
        if '[Content_Types].xml' in entries:
            try:
                ct = ET.fromstring(entries['[Content_Types].xml'])
                ns = {'ct': 'http://schemas.openxmlformats.org/package/2006/content-types'}
                for o in list(ct.findall('ct:Override', ns)):
                    if o.attrib.get('PartName') == '/xl/calcChain.xml':
                        ct.remove(o)
                        changed = True
                entries['[Content_Types].xml'] = ET.tostring(ct, encoding='utf-8', xml_declaration=True)
            except Exception:
                pass

        # remove relationship from xl/_rels/workbook.xml.rels
        if 'xl/_rels/workbook.xml.rels' in entries:
            try:
                wr = ET.fromstring(entries['xl/_rels/workbook.xml.rels'])
                for rel in list(wr):
                    if 'calcChain' in rel.attrib.get('Type', ''):
                        wr.remove(rel)
                        changed = True
                entries['xl/_rels/workbook.xml.rels'] = ET.tostring(wr, encoding='utf-8', xml_declaration=True)
            except Exception:
                pass

        if not changed:
            return

        # write new zip
        with NamedTemporaryFile(delete=False, suffix='.xlsx') as tf:
            temp_path = Path(tf.name)
        try:
            with ZipFile(temp_path, 'w', compression=ZIP_DEFLATED) as zf:
                for name, data in entries.items():
                    zf.writestr(name, data)
            if workbook_path.exists():
                workbook_path.unlink()
            shutil.move(str(temp_path), str(workbook_path))
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    def verify_templates(self) -> dict:
        templates_status = {}
        for template_id in ["1", "2"]:
            try:
                path = self._get_template_path(template_id)
                templates_status[f"Template{template_id}"] = {
                    "exists": True,
                    "path": str(path),
                }
            except FileNotFoundError:
                templates_status[f"Template{template_id}"] = {
                    "exists": False,
                    "path": str(self.templates_dir / settings.TEMPLATES_CONFIG.get(template_id, f"plantilla_{template_id}.xlsx")),
                }
        return templates_status


# Instancia global del servicio
excel_service = ExcelService()
