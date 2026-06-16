"""
Extrae archivos Word (.docx, .doc) de una carpeta origen y copia
al directorio de plantillas del proyecto AutoGeo.

Uso:
    python extract_word_templates.py <carpeta_origen>
    python extract_word_templates.py <carpeta_origen> --dry-run
    python extract_word_templates.py <carpeta_origen> --overwrite
    python extract_word_templates.py <carpeta_origen> --excluir ".venv,node_modules,generated"
"""

import sys
import shutil
import argparse
from pathlib import Path

WORD_EXTENSIONS = {".docx", ".doc"}

DEST_DIR = Path(__file__).parent / "templates" / "word"

DEFAULT_EXCLUDES = {
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "generated",
    ".git",
}


def find_word_files(source: Path, excludes: set[str]) -> list[Path]:
    results = []
    for path in source.rglob("*"):
        if path.suffix.lower() not in WORD_EXTENSIONS:
            continue
        # Descartar si alguna parte de la ruta está en excludes
        if any(part in excludes for part in path.parts):
            continue
        results.append(path)
    return sorted(results)


def copy_word_files(
    source: Path,
    dry_run: bool = False,
    overwrite: bool = False,
    extra_excludes: set[str] | None = None,
) -> None:
    if not source.exists():
        print(f"[ERROR] La carpeta origen no existe: {source}")
        sys.exit(1)

    excludes = DEFAULT_EXCLUDES | (extra_excludes or set())

    DEST_DIR.mkdir(parents=True, exist_ok=True)

    word_files = find_word_files(source, excludes)

    if not word_files:
        print(f"No se encontraron archivos Word en: {source}")
        print(f"Carpetas excluidas: {', '.join(sorted(excludes))}")
        return

    print(f"\nArchivos Word encontrados: {len(word_files)}")
    print(f"Destino: {DEST_DIR}")
    print(f"Carpetas excluidas: {', '.join(sorted(excludes))}\n")

    copied = 0
    skipped = 0

    for src_file in word_files:
        dest_file = DEST_DIR / src_file.name

        if dest_file.exists() and not overwrite:
            print(f"  [OMITIDO]  {src_file.name}")
            print(f"             (ya existe -- usa --overwrite para sobreescribir)")
            skipped += 1
            continue

        action = "COPIANDO" if not dry_run else "SIMULADO"
        print(f"  [{action}]  {src_file.name}")
        print(f"              desde: {src_file.parent}")

        if not dry_run:
            shutil.copy2(src_file, dest_file)
        copied += 1

    print(f"\nResumen:")
    print(f"  Copiados : {copied}")
    print(f"  Omitidos : {skipped}")
    if dry_run:
        print("  (simulacion -- ningun archivo fue copiado realmente)")


def main():
    parser = argparse.ArgumentParser(
        description="Copia archivos Word al directorio de plantillas de AutoGeo"
    )
    parser.add_argument("origen", help="Carpeta desde donde extraer los archivos Word")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra que se copiaría sin hacer cambios reales",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobreescribe archivos que ya existen en el destino",
    )
    parser.add_argument(
        "--excluir",
        default="",
        help="Carpetas adicionales a excluir, separadas por coma (ej: temp,backup)",
    )

    args = parser.parse_args()
    source = Path(args.origen)

    extra_excludes = (
        {e.strip() for e in args.excluir.split(",") if e.strip()}
        if args.excluir
        else set()
    )

    copy_word_files(source, dry_run=args.dry_run, overwrite=args.overwrite, extra_excludes=extra_excludes)


if __name__ == "__main__":
    main()
