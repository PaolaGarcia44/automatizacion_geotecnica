"""Central Visual Resource Manager — AutoGeo

Gestor centralizado de todos los recursos visuales (imágenes, logos, figuras)
utilizados en los documentos Excel y Word generados por el sistema.

Flujo de uso:
  1. Los recursos se declaran una sola vez en _initialize() con sus documentos destino.
  2. Al generar cualquier documento se llama apply_to_excel() / apply_to_word().
  3. El gestor aplica automáticamente cada recurso sin lógica condicional por documento.

Para agregar un recurso nuevo:
  - Definir un ResourceDefinition con su source_path y lista de TargetSpec.
  - Llamar self._register(defn) dentro de _initialize().
  - No tocar ningún otro archivo de servicio.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Set
from zipfile import ZIP_DEFLATED, ZipFile

logger = logging.getLogger(__name__)


# ── Enumeraciones ──────────────────────────────────────────────────────────────

class ResourceType(str, Enum):
    STATIC = "static"        # archivo fijo en disco (logo, sello, firma)
    GENERATED = "generated"  # generado en tiempo de ejecución (SVG, gráfico)
    DYNAMIC = "dynamic"      # aportado por el usuario (fotos de campo)


class InsertMethod(str, Enum):
    XLSX_MEDIA_REPLACE = "xlsx_media_replace"  # reemplaza bytes en xl/media/
    DOCX_MEDIA_REPLACE = "docx_media_replace"  # reemplaza bytes en word/media/
    WIN32COM_COLUMN    = "win32com_column"      # inserta en columna vía win32com (.xls)


# ── Especificación de destino ──────────────────────────────────────────────────

@dataclass
class TargetSpec:
    """Describe dónde y cómo insertar el recurso en un documento concreto.

    Atributos:
        document_ids:  conjunto de template_ids o tipos de documento que reciben el recurso.
        method:        mecanismo de inserción.
        media_entry:   para XLSX/DOCX_MEDIA_REPLACE — ruta interna en el ZIP
                       (ej. "xl/media/image1.JPG").  La búsqueda es insensible a mayúsculas.
        column:        para WIN32COM_COLUMN — letra de la columna destino (ej. "C").
        description:   nota legible para el inventario.
    """
    document_ids: Set[str]
    method: InsertMethod
    media_entry: Optional[str] = None
    column: Optional[str] = None
    description: str = ""


# ── Definición de recurso ──────────────────────────────────────────────────────

@dataclass
class ResourceDefinition:
    """Declara un recurso visual y todos los documentos donde debe aparecer.

    Atributos:
        resource_id:  identificador único (clave del registro).
        name:         nombre legible para el inventario y los logs.
        type:         categoría del recurso.
        targets:      lista de destinos declarados para este recurso.
        source_path:  ruta al archivo fuente para recursos STATIC.
    """
    resource_id: str
    name: str
    type: ResourceType
    targets: List[TargetSpec] = field(default_factory=list)
    source_path: Optional[Path] = None


# ── Gestor central ─────────────────────────────────────────────────────────────

class VisualResourceManager:
    """Administra el ciclo de vida de todos los recursos visuales del sistema."""

    def __init__(self) -> None:
        self._registry: Dict[str, ResourceDefinition] = {}
        self._cache: Dict[str, bytes] = {}
        self._initialized: bool = False

    # ── Inicialización ─────────────────────────────────────────────────────────

    def _initialize(self) -> None:
        """Registra todos los recursos conocidos (ejecutado una sola vez)."""
        if self._initialized:
            return

        from app.core.config import settings

        # ── Imagen corporativa 1 ─────────────────────────────────────────────
        # Presente en los templates de Correlación Geotécnica (plantilla_1/2/3.xlsx).
        # La plantilla ya contiene un ancla de dibujo en columna T.
        # Solo se reemplazan los bytes de la imagen; posición y tamaño permanecen.
        self._register(ResourceDefinition(
            resource_id="logo_imagen1",
            name="Imagen corporativa 1 (Imagen1.jpg)",
            type=ResourceType.STATIC,
            source_path=settings.TEMPLATES_DIR / "imagenes" / "Imagen1.jpg",
            targets=[
                TargetSpec(
                    document_ids={"1", "2", "3"},
                    method=InsertMethod.XLSX_MEDIA_REPLACE,
                    media_entry="xl/media/image1.JPG",
                    description="Logo en columna T — Correlación Geotécnica",
                )
            ],
        ))

        # ── Aquí se agregan futuros recursos ────────────────────────────────
        #
        # Ejemplo — logo en Word:
        # self._register(ResourceDefinition(
        #     resource_id="logo_word",
        #     name="Logo informe Word",
        #     type=ResourceType.STATIC,
        #     source_path=settings.TEMPLATES_DIR / "imagenes" / "LogoWord.png",
        #     targets=[
        #         TargetSpec(
        #             document_ids={"word_informe"},
        #             method=InsertMethod.DOCX_MEDIA_REPLACE,
        #             media_entry="word/media/image1.png",
        #             description="Logo en encabezado del informe Word",
        #         )
        #     ],
        # ))
        #
        # Ejemplo — foto de campo en plantillas P-1/P-2:
        # self._register(ResourceDefinition(
        #     resource_id="foto_campo",
        #     name="Fotografías de campo",
        #     type=ResourceType.DYNAMIC,
        #     targets=[
        #         TargetSpec(
        #             document_ids={"12", "13", "14", "15"},
        #             method=InsertMethod.WIN32COM_COLUMN,
        #             column="C",
        #             description="Fotos de perforación en columna C de P-1/P-2/P-3/P-4",
        #         )
        #     ],
        # ))

        self._initialized = True
        logger.info("ResourceManager inicializado con %d recurso(s).", len(self._registry))

    def _register(self, defn: ResourceDefinition) -> None:
        self._registry[defn.resource_id] = defn
        logger.debug("Recurso registrado: %s — %s", defn.resource_id, defn.name)

    # ── Caché de bytes ─────────────────────────────────────────────────────────

    def _get_bytes(self, defn: ResourceDefinition) -> Optional[bytes]:
        """Devuelve los bytes del recurso, cargándolos del disco si no están en caché."""
        if defn.type != ResourceType.STATIC:
            return None
        if defn.resource_id not in self._cache:
            if defn.source_path and defn.source_path.exists():
                self._cache[defn.resource_id] = defn.source_path.read_bytes()
                logger.debug(
                    "Recurso cargado en caché: %s (%d bytes)",
                    defn.resource_id, len(self._cache[defn.resource_id]),
                )
            else:
                logger.warning("Archivo fuente no encontrado: %s", defn.source_path)
                return None
        return self._cache.get(defn.resource_id)

    def invalidate(self, resource_id: str) -> None:
        """Limpia la caché de un recurso (usar cuando el archivo fuente cambia en disco)."""
        removed = self._cache.pop(resource_id, None)
        if removed is not None:
            logger.debug("Caché limpiada para recurso: %s", resource_id)

    def invalidate_all(self) -> None:
        """Limpia toda la caché."""
        self._cache.clear()
        logger.debug("Caché de recursos limpiada completamente.")

    # ── Inventario ─────────────────────────────────────────────────────────────

    def inventory(self) -> List[dict]:
        """Devuelve el inventario completo de recursos registrados.

        Útil para inspección, debugging y futura exposición vía API.
        """
        self._initialize()
        result = []
        for rid, defn in self._registry.items():
            all_doc_ids: Set[str] = set()
            for t in defn.targets:
                all_doc_ids.update(t.document_ids)
            result.append({
                "id": rid,
                "name": defn.name,
                "type": defn.type.value,
                "source": str(defn.source_path) if defn.source_path else None,
                "source_exists": (
                    defn.source_path.exists() if defn.source_path else None
                ),
                "used_in_documents": sorted(all_doc_ids),
                "targets": [
                    {
                        "method": t.method.value,
                        "document_ids": sorted(t.document_ids),
                        "media_entry": t.media_entry,
                        "column": t.column,
                        "description": t.description,
                    }
                    for t in defn.targets
                ],
            })
        return result

    # ── Escaneo de plantillas ──────────────────────────────────────────────────

    def scan_xlsx(self, template_path: Path) -> List[dict]:
        """Escanea un archivo .xlsx y devuelve info sobre todas las imágenes embebidas."""
        results = []
        try:
            with ZipFile(template_path, "r") as zf:
                for name in zf.namelist():
                    if not name.startswith("xl/media/"):
                        continue
                    ext = Path(name).suffix.lower()
                    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".emf", ".wmf", ".svg"}:
                        continue
                    data = zf.read(name)
                    results.append({
                        "template": template_path.name,
                        "entry": name,
                        "size_kb": round(len(data) / 1024, 1),
                        "format": ext.lstrip(".").upper(),
                    })
        except Exception:
            logger.debug("Error escaneando %s", template_path.name, exc_info=True)
        return results

    def scan_docx(self, template_path: Path) -> List[dict]:
        """Escanea un archivo .docx y devuelve info sobre todas las imágenes embebidas."""
        results = []
        try:
            with ZipFile(template_path, "r") as zf:
                for name in zf.namelist():
                    if not name.startswith("word/media/"):
                        continue
                    ext = Path(name).suffix.lower()
                    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".emf", ".wmf", ".svg"}:
                        continue
                    data = zf.read(name)
                    results.append({
                        "template": template_path.name,
                        "entry": name,
                        "size_kb": round(len(data) / 1024, 1),
                        "format": ext.lstrip(".").upper(),
                    })
        except Exception:
            logger.debug("Error escaneando %s", template_path.name, exc_info=True)
        return results

    def scan_all_templates(self, templates_dir: Optional[Path] = None) -> List[dict]:
        """Escanea todas las plantillas y devuelve el inventario completo de imágenes.

        Recorre recursivamente templates_dir (o settings.TEMPLATES_DIR por defecto)
        buscando archivos .xlsx y .docx, e informa todas las imágenes encontradas.
        """
        if templates_dir is None:
            from app.core.config import settings
            templates_dir = settings.TEMPLATES_DIR

        all_results: List[dict] = []
        for path in sorted(templates_dir.rglob("*")):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix in {".xlsx", ".xlsm"}:
                all_results.extend(self.scan_xlsx(path))
            elif suffix in {".docx"}:
                all_results.extend(self.scan_docx(path))
        return all_results

    # ── Reemplazo genérico de media ────────────────────────────────────────────

    def _replace_zip_media(
        self, work_file: Path, media_entry: str, img_bytes: bytes
    ) -> bool:
        """Reemplaza los bytes de una entrada de imagen dentro de un ZIP (xlsx o docx).

        La búsqueda de la entrada es insensible a mayúsculas/minúsculas.
        No modifica posición, tamaño ni ningún otro elemento del documento.
        Devuelve True si el reemplazo tuvo éxito.
        """
        try:
            with ZipFile(work_file, "r") as src:
                entries = [(info, src.read(info.filename)) for info in src.infolist()]
        except Exception:
            logger.error("No se pudo leer el archivo: %s", work_file, exc_info=True)
            return False

        replaced = False
        updated = []
        for info, data in entries:
            if info.filename.lower() == media_entry.lower():
                updated.append((info, img_bytes))
                replaced = True
            else:
                updated.append((info, data))

        if not replaced:
            logger.warning(
                "Entrada '%s' no encontrada en %s — recurso omitido.",
                media_entry, work_file.name,
            )
            return False

        with NamedTemporaryFile(delete=False, suffix=work_file.suffix) as tf:
            temp_path = Path(tf.name)
        try:
            with ZipFile(temp_path, "w", compression=ZIP_DEFLATED) as zf:
                for info, data in updated:
                    zf.writestr(info, data)
            if work_file.exists():
                work_file.unlink()
            shutil.move(str(temp_path), str(work_file))
            logger.debug("Recurso visual aplicado: '%s' → %s", media_entry, work_file.name)
            return True
        except Exception:
            logger.error(
                "Error escribiendo recurso en %s", work_file.name, exc_info=True
            )
            return False
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

    # ── Aplicación a documentos ────────────────────────────────────────────────

    def apply_to_excel(self, work_file: Path, template_id: str) -> None:
        """Aplica todos los recursos estáticos registrados para este template_id.

        Recorre el registro y aplica automáticamente cada recurso cuya lista
        de document_ids incluya template_id.  No se requiere ningún condicional
        específico por documento en el código que llama a este método.
        """
        self._initialize()
        applied = 0
        for resource_id, defn in self._registry.items():
            if defn.type != ResourceType.STATIC:
                continue
            for target in defn.targets:
                if template_id not in target.document_ids:
                    continue
                if target.method == InsertMethod.XLSX_MEDIA_REPLACE:
                    img_bytes = self._get_bytes(defn)
                    if img_bytes is None:
                        logger.warning(
                            "Recurso '%s' sin bytes; omitido para template %s.",
                            resource_id, template_id,
                        )
                        continue
                    if self._replace_zip_media(work_file, target.media_entry, img_bytes):
                        applied += 1
        if applied:
            logger.info(
                "%d recurso(s) visual(es) aplicado(s) a template %s (%s).",
                applied, template_id, work_file.name,
            )

    def apply_to_word(self, work_file: Path, document_id: str = "word_informe") -> None:
        """Aplica todos los recursos estáticos registrados para documentos Word.

        document_id identifica el tipo de documento Word (por defecto "word_informe").
        Actualmente no hay recursos Word declarados; este método está listo para
        cuando se definan plantillas con imágenes reemplazables.
        """
        self._initialize()
        applied = 0
        for resource_id, defn in self._registry.items():
            if defn.type != ResourceType.STATIC:
                continue
            for target in defn.targets:
                if document_id not in target.document_ids:
                    continue
                if target.method == InsertMethod.DOCX_MEDIA_REPLACE:
                    img_bytes = self._get_bytes(defn)
                    if img_bytes is None:
                        logger.warning(
                            "Recurso Word '%s' sin bytes; omitido.", resource_id
                        )
                        continue
                    if self._replace_zip_media(work_file, target.media_entry, img_bytes):
                        applied += 1
        if applied:
            logger.info(
                "%d recurso(s) visual(es) aplicado(s) al informe Word (%s).",
                applied, work_file.name,
            )


# ── Instancia global ───────────────────────────────────────────────────────────

resource_manager = VisualResourceManager()
