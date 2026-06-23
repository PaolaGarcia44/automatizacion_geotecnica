"""
1. Copia archivos .doc/.docx de E:\\EDWIN que contengan "INFORME" + un municipio/departamento colombiano.
2. Elimina de la carpeta destino los archivos que NO cumplan esa condición.
"""

import os
import re
import shutil
import unicodedata
from pathlib import Path

ORIGEN  = Path(r"E:\EDWIN")
DESTINO = Path(
    r"C:\Users\Paola\OneDrive - Tecnologico de Antioquia Institucion Universitaria"
    r"\Escritorio\Automatización geotecnica\automatizacion_geotecnica"
    r"\backend\templates\word"
)

EXTENSIONES = {".doc", ".docx"}

# ---------------------------------------------------------------------------
# Lista de municipios y departamentos de Colombia
# ---------------------------------------------------------------------------
LUGARES_RAW = [
    # Departamentos
    "AMAZONAS","ANTIOQUIA","ARAUCA","ATLANTICO","BOLIVAR","BOYACA","CALDAS",
    "CAQUETA","CASANARE","CAUCA","CESAR","CHOCO","CORDOBA","CUNDINAMARCA",
    "GUAINIA","GUAVIARE","HUILA","LA GUAJIRA","MAGDALENA","META","NARINO",
    "NORTE DE SANTANDER","PUTUMAYO","QUINDIO","RISARALDA","SAN ANDRES",
    "SANTANDER","SUCRE","TOLIMA","VALLE DEL CAUCA","VAUPES","VICHADA","BOGOTA",

    # Municipios de Antioquia
    "ABEJORRAL","ABRIAQUI","ALEJANDRIA","AMAGA","ANDES","ANGOSTURA","ANZA",
    "APARTADO","ARBOLETES","ARGELIA","BARBOSA","BELLO","BETANIA","BETULIA",
    "BRICENO","BURITICA","CACERES","CAICEDO","CAMPAMENTO","CANASGORDAS",
    "CARACOLI","CARAMANTA","CAREPA","EL CARMEN","EL CARMEN DE VIBORAL",
    "CAROLINA","CAUCASIA","CHIGORODO","CISNEROS","COCORNA","CONCEPCION",
    "CONCORDIA","COPACABANA","DABEIBA","DON MATIAS","EBEJICO","EL BAGRE",
    "ENTRERRIOS","ENTRERIOS","ENVIGADO","FREDONIA","FRONTINO","GIRALDO",
    "GIRARDOTA","GOMEZ PLATA","GRANADA","GUADALUPE","GUARNE","GUATAPE",
    "HELICONIA","HISPANIA","ITAGUI","ITUANGO","JARDIN","JERICO",
    "LA CEJA","LA ESTRELLA","LA PINTADA","LA UNION","LIBORINA","MACEO",
    "MARINILLA","MEDELLIN","MONTEBELLO","MURINDO","MUTATA","NECHI","NECOCLI",
    "OLAYA","PENOL","PEQUE","PUEBLORRICO","PUERTO BERRIO","PUERTO NARE",
    "PUERTO TRIUNFO","REMEDIOS","EL RETIRO","RETIRO","RIONEGRO","SABANETA",
    "SALGAR","SAN ANDRES DE CUERQUIA","SAN CARLOS","SAN FRANCISCO",
    "SAN JERONIMO","SAN JOSE DE LA MONTANA","SAN JUAN DE URABA","SAN LUIS",
    "SAN PEDRO","SAN RAFAEL","SAN ROQUE","SAN VICENTE","SANTA BARBARA",
    "SANTA FE DE ANTIOQUIA","SANTA ROSA","SANTO DOMINGO","EL SANTUARIO",
    "SANTUARIO","SEGOVIA","SONSON","SOPETRAN","TAMESIS","TARAZA","TARSO",
    "TITIRIBÍ","TITIRIBÍ","TOLEDO","TURBO","URAMITA","URRAO","VALDIVIA",
    "VALPARAISO","VEGACHI","VENECIA","VIGIA DEL FUERTE","YALI","YARUMAL",
    "YOLOMBO","YONDO","ZARAGOZA","ANGELOPOLIS","ANZÁ",

    # Corregimientos / sectores de Medellín (se usan como municipios en informes)
    "SAN ANTONIO DE PRADO","SANTA ELENA","SAN CRISTOBAL","ALTAVISTA",
    "SAN SEBASTIAN DE PALMITAS","LLANOGRANDE",

    # Barrios / sectores urbanos frecuentes en informes de Medellín
    "MANRIQUE","LAURELES","BELEN","CASTILLA","BUENOS AIRES","LA AMERICA",
    "VILLA HERMOSA","NIQUIA","EL POBLADO","ARANJUEZ","LA CANDELARIA",
    "GUAYABAL","SAN JAVIER","ROBLEDO","CAMPO AMOR","BELEN ALTAVISTA",

    # Otros municipios colombianos presentes en los archivos
    "BUGA","PUERTO BOYACA","CURRULAO","PORTACHUELO","PUERTO ESCONDIDO",
    "SAN MARTIN","ALEJANDRÍA",
]


def _norm(texto: str) -> str:
    """Elimina acentos y convierte a mayúsculas para comparación."""
    return "".join(
        c for c in unicodedata.normalize("NFD", texto.upper())
        if unicodedata.category(c) != "Mn"
    )


# Construir conjunto normalizado para búsqueda O(1) aproximada
LUGARES_NORM = [_norm(l) for l in LUGARES_RAW]


def tiene_municipio(nombre_stem: str) -> bool:
    """True si el stem del archivo contiene al menos un municipio/departamento."""
    nombre_norm = _norm(nombre_stem)
    for lugar in LUGARES_NORM:
        # Verificar que el lugar aparezca como palabra(s) completa(s)
        patron = r"(?:^|[^A-Z])" + re.escape(lugar) + r"(?:[^A-Z]|$)"
        if re.search(patron, nombre_norm):
            return True
    return False


def es_valido(nombre_stem: str) -> bool:
    """True si el archivo tiene INFORME + al menos un municipio/departamento."""
    return "INFORME" in _norm(nombre_stem) and tiene_municipio(nombre_stem)


# ---------------------------------------------------------------------------
# Paso 1: Copiar desde E:\EDWIN los archivos válidos
# ---------------------------------------------------------------------------
def copiar_desde_origen():
    DESTINO.mkdir(parents=True, exist_ok=True)
    copiados = omitidos = ignorados = 0

    print(f"\n{'='*60}")
    print("PASO 1 — Copiando desde E:\\EDWIN")
    print(f"{'='*60}")

    for ruta in ORIGEN.rglob("*"):
        if not ruta.is_file() or ruta.suffix.lower() not in EXTENSIONES:
            continue
        if not es_valido(ruta.stem):
            ignorados += 1
            continue

        destino_archivo = DESTINO / ruta.name
        if destino_archivo.exists():
            omitidos += 1
            continue

        shutil.copy2(ruta, destino_archivo)
        copiados += 1
        print(f"  [COPIADO] {ruta.relative_to(ORIGEN)}")

    print(f"\n  Copiados: {copiados}  |  Ya existían: {omitidos}  |  Sin municipio (ignorados): {ignorados}")


# ---------------------------------------------------------------------------
# Paso 2: Eliminar del destino los que no cumplan la condición
# ---------------------------------------------------------------------------
def limpiar_destino():
    print(f"\n{'='*60}")
    print("PASO 2 — Limpiando carpeta destino")
    print(f"{'='*60}")

    eliminados = conservados = 0

    for archivo in sorted(DESTINO.iterdir()):
        if not archivo.is_file() or archivo.suffix.lower() not in EXTENSIONES:
            continue
        if es_valido(archivo.stem):
            conservados += 1
        else:
            print(f"  [ELIMINADO] {archivo.name}")
            archivo.unlink()
            eliminados += 1

    print(f"\n  Conservados: {conservados}  |  Eliminados: {eliminados}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    copiar_desde_origen()
    limpiar_destino()
    print("\nListo.")
