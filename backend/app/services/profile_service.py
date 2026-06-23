"""
StratigraphicProfileService
===========================
Offline, standalone stratigraphic profile generator for geotechnical studies.

Design principles
-----------------
* **Zero mandatory external dependencies** — the SVG output path uses only the
  Python standard library (math, unicodedata, pathlib).
* **Completely offline** — no network calls, no cloud services, no AutoCAD.
* **Library-first** — import ``profile_service`` from any Python desktop
  application, CLI tool, PyInstaller-packaged executable, or Electron main
  process without touching the FastAPI layer.
* **Optional richer exports** — PDF and PNG conversion will be attempted with
  *cairosvg* first, then *svglib + reportlab*.  If neither is installed the
  method raises a clear ``RuntimeError`` with install instructions.

CLI usage (standalone, no web server required)::

    python profile_service.py --input datos.json --output perfil.svg
    python profile_service.py -i datos.json -o perfil.pdf --project "OBRA X"

Input JSON format::

    [
      {"profundidad_z": 0.40, "tipo_suelo_principal": "Relleno",
       "color_predominante": "Café oscuro", "descripcion_suelo": "..."},
      ...
    ]

PyInstaller packaging
---------------------
All imports used by SVG generation are from the stdlib — no hidden DLLs.
For PDF/PNG export bundle *cairosvg* with its Cairo DLLs, or *svglib* +
*reportlab* (pure-Python wheels, no native dependencies on Windows).
"""
from __future__ import annotations

import math
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

__all__ = ["StratigraphicProfileService", "profile_service"]


# ── text helpers ──────────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    nfkd = unicodedata.normalize("NFD", text or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def _esc(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _is_dark(hex6: str) -> bool:
    try:
        r, g, b = int(hex6[:2], 16), int(hex6[2:4], 16), int(hex6[4:], 16)
        return (r * 299 + g * 587 + b * 114) / 1000 < 140
    except Exception:
        return False


def _wrap(text: str, max_chars: int) -> List[str]:
    words = (text or "").split()
    lines: List[str] = []
    line = ""
    for w in words:
        if not line:
            line = w
        elif len(line) + 1 + len(w) <= max_chars:
            line += " " + w
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines or [""]


# ── color map (mirrors excel_service._COLOR_MAP, normalized keys) ─────────────

_COLOR_MAP: Dict[str, str] = {
    "beige": "F5F0D7", "beis": "F5F0D7",
    "cafe": "8B5A2B", "cafe oscuro": "5C3D2E", "cafe claro": "A0826D",
    "cafe rojizo": "9B6B4A",
    "amarillo": "FFD966", "amarillo claro": "FFEB3B", "amarillo oscuro": "D4A520",
    "amarillo cafe": "9B8C00",
    "rojizo": "C0504D", "rojo": "FF0000", "rojo oscuro": "8B0000",
    "blanco": "FFFFFF", "blanco sucio": "E8E8E8",
    "gris": "808080", "gris claro": "D9D9D9", "gris oscuro": "505050",
    "gris azuloso": "708090", "gris amarillento": "A9A9A9",
    "naranja": "F4B183", "naranja claro": "FFD700", "naranja oscuro": "FF8C00",
    "verde": "92D050", "verde claro": "C6E0B4", "verde oscuro": "008000",
    "marron": "8B4513", "marron claro": "A0826D", "marron oscuro": "5C3D2E",
    "marron rojizo": "9B6B4A",
    "negro": "000000", "negro verdoso": "1B4D3E",
    "rosa": "FFC0CB", "purpura": "800080", "violeta": "EE82EE",
    "azul": "0000FF", "azul claro": "ADD8E6", "azul oscuro": "00008B",
    "turquesa": "40E0D0", "cian": "00FFFF",
    "crema": "FFFDD0", "mostaza": "FFDB58", "ocre": "CC7000",
    "siena": "A0522D", "tostado": "D2B48C", "leonado": "DAA520",
    "grisaceo": "A9A9A9", "pardusco": "8B7355",
    "oscuro": "505050", "claro": "E8E8E8",
}

_SOIL_DEFAULTS: Dict[str, str] = {
    "clay":        "C4A882",
    "silt":        "D4C5A9",
    "fine_sand":   "EDD9A3",
    "medium_sand": "E8CB87",
    "coarse_sand": "D4B870",
    "gravel":      "B8A898",
    "rock":        "9898A8",
    "fill":        "C8B4A0",
    "organic":     "8B9B5A",
    "unknown":     "D0C0B0",
}

_SOIL_LABELS: Dict[str, str] = {
    "clay":        "Arcilla",
    "silt":        "Limo",
    "fine_sand":   "Arena fina",
    "medium_sand": "Arena",
    "coarse_sand": "Arena gruesa",
    "gravel":      "Grava",
    "rock":        "Roca",
    "fill":        "Relleno",
    "organic":     "Suelo orgánico",
    "unknown":     "Suelo",
}

# Most-specific keywords first
_SOIL_CLASSIFIERS: List[Tuple[str, str]] = [
    ("arena fina",       "fine_sand"),
    ("arena media",      "medium_sand"),
    ("arena gruesa",     "coarse_sand"),
    ("arena limosa",     "medium_sand"),
    ("arena arcillosa",  "medium_sand"),
    ("arena",            "medium_sand"),
    ("arcillo",          "clay"),
    ("arcilla",          "clay"),
    ("limo arcill",      "silt"),
    ("limo arenos",      "silt"),
    ("limo",             "silt"),
    ("gravilla",         "gravel"),
    ("grava",            "gravel"),
    ("roca",             "rock"),
    ("relleno",          "fill"),
    ("suelo org",        "organic"),
    ("organico",         "organic"),
    ("organica",         "organic"),
    ("turba",            "organic"),
    # USCS codes (appear in parentheses or alone)
    ("(ch)", "clay"),  ("(cl)", "clay"),
    ("(mh)", "silt"),  ("(ml)", "silt"),
    ("(sm)", "medium_sand"), ("(sc)", "medium_sand"),
    ("(sp)", "coarse_sand"), ("(sw)", "medium_sand"),
    ("(gm)", "gravel"), ("(gp)", "gravel"), ("(gw)", "gravel"),
]

# SVG <pattern> snippets — semi-transparent overlays, work on any background color
_PATTERN_DEFS: Dict[str, str] = {
    "clay": (
        '<pattern id="pat_clay" patternUnits="userSpaceOnUse" width="30" height="5">'
        '<line x1="0" y1="2.5" x2="30" y2="2.5" stroke="rgba(0,0,0,0.22)" stroke-width="0.9"/>'
        '</pattern>'
    ),
    "silt": (
        '<pattern id="pat_silt" patternUnits="userSpaceOnUse" width="12" height="5">'
        '<line x1="0" y1="2.5" x2="8" y2="2.5" stroke="rgba(0,0,0,0.20)" stroke-width="0.8"/>'
        '</pattern>'
    ),
    "fine_sand": (
        '<pattern id="pat_fine_sand" patternUnits="userSpaceOnUse" width="6" height="6">'
        '<circle cx="3" cy="3" r="0.75" fill="rgba(0,0,0,0.30)"/>'
        '</pattern>'
    ),
    "medium_sand": (
        '<pattern id="pat_medium_sand" patternUnits="userSpaceOnUse" width="8" height="8">'
        '<circle cx="2" cy="2" r="1.0" fill="rgba(0,0,0,0.28)"/>'
        '<circle cx="6" cy="6" r="1.0" fill="rgba(0,0,0,0.28)"/>'
        '</pattern>'
    ),
    "coarse_sand": (
        '<pattern id="pat_coarse_sand" patternUnits="userSpaceOnUse" width="10" height="10">'
        '<circle cx="3" cy="3" r="1.6" fill="rgba(0,0,0,0.25)"/>'
        '<circle cx="8" cy="8" r="1.6" fill="rgba(0,0,0,0.25)"/>'
        '</pattern>'
    ),
    "gravel": (
        '<pattern id="pat_gravel" patternUnits="userSpaceOnUse" width="26" height="18">'
        '<ellipse cx="7" cy="5" rx="5.5" ry="3.5" fill="none" stroke="rgba(0,0,0,0.45)" stroke-width="1.0"/>'
        '<ellipse cx="19" cy="12" rx="5.0" ry="3.2" fill="none" stroke="rgba(0,0,0,0.40)" stroke-width="0.9"/>'
        '<ellipse cx="5" cy="15" rx="3.5" ry="2.2" fill="none" stroke="rgba(0,0,0,0.38)" stroke-width="0.8"/>'
        '</pattern>'
    ),
    "rock": (
        '<pattern id="pat_rock" patternUnits="userSpaceOnUse" width="14" height="14">'
        '<line x1="0" y1="0" x2="14" y2="14" stroke="rgba(0,0,0,0.30)" stroke-width="0.9"/>'
        '<line x1="14" y1="0" x2="0" y2="14" stroke="rgba(0,0,0,0.30)" stroke-width="0.9"/>'
        '</pattern>'
    ),
    "fill": (
        '<pattern id="pat_fill" patternUnits="userSpaceOnUse" width="12" height="12">'
        '<line x1="0" y1="12" x2="12" y2="0" stroke="rgba(0,0,0,0.26)" stroke-width="1.3"/>'
        '<line x1="-6" y1="12" x2="6" y2="0" stroke="rgba(0,0,0,0.14)" stroke-width="0.6"/>'
        '<line x1="6" y1="12" x2="18" y2="0" stroke="rgba(0,0,0,0.14)" stroke-width="0.6"/>'
        '</pattern>'
    ),
    "organic": (
        '<pattern id="pat_organic" patternUnits="userSpaceOnUse" width="24" height="8">'
        '<path d="M0,4 Q6,1 12,4 Q18,7 24,4" fill="none" stroke="rgba(0,0,0,0.30)" stroke-width="1.0"/>'
        '</pattern>'
    ),
    "unknown": (
        '<pattern id="pat_unknown" patternUnits="userSpaceOnUse" width="10" height="10">'
        '<line x1="0" y1="10" x2="10" y2="0" stroke="rgba(0,0,0,0.18)" stroke-width="0.8"/>'
        '</pattern>'
    ),
}


def _classify_soil(tipo: Optional[str], desc: Optional[str]) -> str:
    for text in (tipo, desc):
        if not text:
            continue
        n = _norm(text)
        for kw, sc in _SOIL_CLASSIFIERS:
            if kw in n:
                return sc
    return "unknown"


def _fill_color(color_name: Optional[str], soil_class: str) -> str:
    if color_name:
        n = _norm(color_name)
        hit = next((v for k, v in _COLOR_MAP.items() if _norm(k) == n), None)
        if not hit:
            hit = next((v for k, v in _COLOR_MAP.items() if _norm(k) in n or n in _norm(k)), None)
        if hit:
            return hit
    return _SOIL_DEFAULTS.get(soil_class, "D0C0B0")


# ── main service ──────────────────────────────────────────────────────────────

class StratigraphicProfileService:
    """
    Generates professional SVG stratigraphic profiles.

    Usage::

        from app.services.profile_service import profile_service
        path = profile_service.save_profile(
            perforaciones=perforaciones_list,
            output_path=Path("generated/perfil.svg"),
            project_name="PROYECTO X - MEDELLÍN",
            sondeo="P-1",
            fecha=date.today(),
        )
    """

    # ── Canvas / layout (px) ──────────────────────────────────────────────────
    W = 820          # total width

    SC_X  = 35       # scale column: left edge
    SC_W  = 60       # scale column: width

    PF_X  = 98       # profile column: left  (SC_X + SC_W + 3)
    PF_W  = 116      # profile column: width

    ESP_X = 218      # espesor column: left  (PF_X + PF_W + 4)
    ESP_W = 52       # espesor column: width

    DESC_X = 274     # description column: left  (ESP_X + ESP_W + 4)
    DESC_W = 511     # description column: width  → right edge = 785 = W - 35

    HEADER_H    = 80
    COL_HDR_H   = 30
    LEG_MARGIN  = 22
    LEG_ITEM_H  = 26
    LEG_SWATCH  = 16
    LEG_COLS    = 3

    FF = "Arial, Helvetica, sans-serif"

    # Palette
    C_HDR_DARK  = "#1C3A5C"
    C_HDR_MID   = "#2D5E8C"
    C_COL_HDR   = "#3A6FA3"
    C_COL_HDR_T = "#FFFFFF"
    C_BORDER    = "#3A3A3A"
    C_GRID      = "#C8C8C8"
    C_BOUND     = "#404040"
    C_SCALE_T   = "#2A2A2A"
    C_DESC_T    = "#1A1A1A"
    C_LEG_BG    = "#F7F7F5"
    C_LEG_BD    = "#CCCCCC"

    # ── scale helpers ─────────────────────────────────────────────────────────

    def _scale_interval(self, depth: float) -> float:
        if depth <= 3.0:   return 0.25
        if depth <= 8.0:   return 0.5
        if depth <= 20.0:  return 1.0
        return 2.0

    def _ppm(self, depth: float) -> float:
        """Pixels per metre — targets a profile body of 500–1 000 px."""
        target = max(500.0, min(1000.0, 100.0 * depth))
        return round(target / depth, 3)

    # ── layer builder ─────────────────────────────────────────────────────────

    def _build_layers(self, perforaciones: List[Dict]) -> List[Dict]:
        layers: List[Dict] = []
        prev = 0.0
        for item in (perforaciones or []):
            try:
                end = float(str(item.get("profundidad_z") or 0).replace(",", "."))
            except Exception:
                end = prev + 1.0
            if end <= prev:
                end = prev + 0.5

            tipo  = str(item.get("tipo_suelo_principal") or "").strip()
            desc  = str(item.get("descripcion_suelo")    or tipo).strip()
            color = str(item.get("color_predominante")   or "").strip()
            sc    = _classify_soil(tipo, desc)
            hex6  = _fill_color(color, sc)

            layers.append({
                "d0":    prev,
                "d1":    end,
                "esp":   round(end - prev, 3),
                "sc":    sc,
                "hex":   hex6,
                "desc":  desc or tipo or _SOIL_LABELS.get(sc, "Suelo"),
                "color_name": color,
            })
            prev = end
        return layers

    # ── SVG section builders ──────────────────────────────────────────────────

    def _defs(self, used: Set[str], profile_x: int, profile_y: int,
              profile_w: int, profile_h: float,
              desc_x: int, desc_w: int, total_h: int) -> str:
        parts = ["<defs>"]
        for sc in used:
            if sc in _PATTERN_DEFS:
                parts.append("  " + _PATTERN_DEFS[sc])
        # Clip path for the profile column (prevents patterns bleeding into margins)
        parts.append(
            f'  <clipPath id="cp_profile">'
            f'<rect x="{profile_x}" y="{profile_y}" '
            f'width="{profile_w}" height="{profile_h:.1f}"/></clipPath>'
        )
        # Clip path for description column
        parts.append(
            f'  <clipPath id="cp_desc">'
            f'<rect x="{desc_x}" y="{profile_y}" '
            f'width="{desc_w}" height="{profile_h:.1f}"/></clipPath>'
        )
        parts.append("</defs>")
        return "\n".join(parts)

    def _header(self, project: str, sondeo: str, fecha: str) -> str:
        w  = self.W
        h1 = 42   # title bar height
        h2 = self.HEADER_H - h1  # info bar height
        return "\n".join([
            f'<rect x="0" y="0" width="{w}" height="{h1}" fill="{self.C_HDR_DARK}"/>',
            f'<text x="{w//2}" y="28" text-anchor="middle" font-family="{self.FF}" '
            f'font-size="15" font-weight="bold" letter-spacing="1" fill="#FFFFFF">'
            f'PERFIL ESTRATIGRÁFICO DEL SUELO</text>',
            f'<rect x="0" y="{h1}" width="{w}" height="{h2}" fill="{self.C_HDR_MID}"/>',
            # Project label
            f'<text x="14" y="{h1+14}" font-family="{self.FF}" font-size="8" '
            f'font-weight="bold" fill="#FFFFFF">PROYECTO:</text>',
            f'<text x="78" y="{h1+14}" font-family="{self.FF}" font-size="8" '
            f'fill="#FFFFFF">{_esc(project)}</text>',
            # Sondeo (center)
            f'<text x="{w//2}" y="{h1+14}" text-anchor="middle" font-family="{self.FF}" '
            f'font-size="8" fill="#FFFFFF">'
            f'<tspan font-weight="bold">SONDEO: </tspan>{_esc(sondeo)}</text>',
            # Date (right)
            f'<text x="{w-14}" y="{h1+14}" text-anchor="end" font-family="{self.FF}" '
            f'font-size="8" fill="#FFFFFF">'
            f'<tspan font-weight="bold">FECHA: </tspan>{_esc(fecha)}</text>',
            # Tagline
            f'<text x="14" y="{h1+28}" font-family="{self.FF}" font-size="7" '
            f'fill="rgba(255,255,255,0.75)">AutoGeo — Generación dinámica de perfil estratigráfico</text>',
        ])

    def _col_headers(self, y0: int) -> str:
        h  = self.COL_HDR_H
        w  = self.W
        re = self.DESC_X + self.DESC_W   # right edge
        parts = [
            f'<rect x="{self.SC_X}" y="{y0}" width="{re - self.SC_X}" height="{h}" fill="{self.C_COL_HDR}"/>',
        ]
        # Column labels
        cols = [
            (self.SC_X,   self.SC_W,   "Prof. (m)",               "middle"),
            (self.PF_X,   self.PF_W,   "Perfil gráfico",          "middle"),
            (self.ESP_X,  self.ESP_W,  "Esp. (m)",                "middle"),
            (self.DESC_X, self.DESC_W, "Descripción macroscópica", "start"),
        ]
        for cx, cw, label, anchor in cols:
            tx = cx + cw // 2 if anchor == "middle" else cx + 6
            parts.append(
                f'<text x="{tx}" y="{y0 + h//2 + 4}" text-anchor="{anchor}" '
                f'font-family="{self.FF}" font-size="8.5" font-weight="bold" '
                f'fill="{self.C_COL_HDR_T}">{_esc(label)}</text>'
            )
        # Vertical dividers
        for vx in (self.PF_X, self.ESP_X, self.DESC_X, re):
            parts.append(
                f'<line x1="{vx}" y1="{y0}" x2="{vx}" y2="{y0+h}" '
                f'stroke="rgba(255,255,255,0.4)" stroke-width="0.6"/>'
            )
        # Bottom separator
        parts.append(
            f'<line x1="{self.SC_X}" y1="{y0+h}" x2="{re}" y2="{y0+h}" '
            f'stroke="{self.C_BORDER}" stroke-width="1.2"/>'
        )
        return "\n".join(parts)

    def _profile_body(
        self,
        layers: List[Dict],
        total_depth: float,
        ppm: float,
        y0: int,
    ) -> str:
        interval  = self._scale_interval(total_depth)
        re        = self.DESC_X + self.DESC_W
        profile_h = total_depth * ppm
        parts: List[str] = []

        # ── background ────────────────────────────────────────────────────────
        parts.append(
            f'<rect x="{self.SC_X}" y="{y0}" width="{re - self.SC_X}" '
            f'height="{profile_h:.1f}" fill="white"/>'
        )

        # ── grid lines at scale intervals ─────────────────────────────────────
        d = 0.0
        while d <= total_depth + 1e-9:
            gy = y0 + d * ppm
            parts.append(
                f'<line x1="{self.SC_X}" y1="{gy:.2f}" x2="{re}" y2="{gy:.2f}" '
                f'stroke="{self.C_GRID}" stroke-width="0.4" stroke-dasharray="4,3"/>'
            )
            d = round(d + interval, 10)

        # ── strata ────────────────────────────────────────────────────────────
        chars_line = max(30, int(self.DESC_W / 5.0))
        line_h     = 11.5

        for layer in layers:
            d0, d1 = layer["d0"], layer["d1"]
            ys = y0 + d0 * ppm
            lh = (d1 - d0) * ppm
            sc = layer["sc"]
            fc = "#" + layer["hex"]

            # Colored fill
            parts.append(
                f'<rect x="{self.PF_X}" y="{ys:.2f}" width="{self.PF_W}" '
                f'height="{lh:.2f}" fill="{fc}"/>'
            )
            # Pattern overlay (clipped)
            parts.append(
                f'<rect x="{self.PF_X}" y="{ys:.2f}" width="{self.PF_W}" '
                f'height="{lh:.2f}" fill="url(#pat_{sc})" clip-path="url(#cp_profile)"/>'
            )
            # Top boundary
            parts.append(
                f'<line x1="{self.PF_X}" y1="{ys:.2f}" x2="{self.PF_X+self.PF_W}" '
                f'y2="{ys:.2f}" stroke="{self.C_BOUND}" stroke-width="1.3"/>'
            )
            # Soil type label inside profile column
            if lh > 20:
                label = _SOIL_LABELS.get(sc, "Suelo")
                fg    = "#FFFFFF" if _is_dark(layer["hex"]) else "#1F2937"
                lx    = self.PF_X + self.PF_W // 2
                ly    = ys + lh / 2 + 4
                parts.append(
                    f'<text x="{lx}" y="{ly:.1f}" text-anchor="middle" '
                    f'font-family="{self.FF}" font-size="7.5" font-style="italic" '
                    f'fill="{fg}" opacity="0.9">{_esc(label)}</text>'
                )

            # Espesor centered
            ecx = self.ESP_X + self.ESP_W // 2
            ecy = ys + lh / 2 + 4
            parts.append(
                f'<text x="{ecx}" y="{ecy:.1f}" text-anchor="middle" '
                f'font-family="{self.FF}" font-size="9" font-weight="bold" '
                f'fill="{self.C_DESC_T}">{layer["esp"]:.2f}</text>'
            )

            # Description text (multi-line, clipped)
            if lh >= line_h:
                wrapped   = _wrap(layer["desc"], chars_line)
                max_lines = max(1, int(lh / line_h))
                visible   = wrapped[:max_lines]
                text_top  = ys + max(line_h, (lh - len(visible) * line_h) / 2)
                parts.append(
                    f'<text x="{self.DESC_X + 6}" y="{text_top:.1f}" '
                    f'font-family="{self.FF}" font-size="8.5" fill="{self.C_DESC_T}" '
                    f'clip-path="url(#cp_desc)">'
                )
                for i, ln in enumerate(visible):
                    dy = "" if i == 0 else f' dy="{line_h:.1f}"'
                    parts.append(f'  <tspan x="{self.DESC_X + 6}"{dy}>{_esc(ln)}</tspan>')
                parts.append("</text>")
                if len(wrapped) > max_lines:
                    ey = text_top + (max_lines - 1) * line_h
                    parts.append(
                        f'<text x="{self.DESC_X + self.DESC_W - 8}" y="{ey:.1f}" '
                        f'text-anchor="end" font-family="{self.FF}" font-size="8.5" '
                        f'fill="#999">…</text>'
                    )

        # ── bottom boundary ───────────────────────────────────────────────────
        yb = y0 + total_depth * ppm
        parts.append(
            f'<line x1="{self.PF_X}" y1="{yb:.2f}" x2="{self.PF_X+self.PF_W}" '
            f'y2="{yb:.2f}" stroke="{self.C_BOUND}" stroke-width="1.8"/>'
        )

        # ── depth scale ───────────────────────────────────────────────────────
        d = 0.0
        while d <= total_depth + 1e-9:
            sy = y0 + d * ppm
            # Tick
            parts.append(
                f'<line x1="{self.PF_X - 5}" y1="{sy:.2f}" x2="{self.PF_X}" '
                f'y2="{sy:.2f}" stroke="{self.C_BOUND}" stroke-width="1.2"/>'
            )
            # Label (right-aligned, before tick)
            parts.append(
                f'<text x="{self.PF_X - 8}" y="{sy + 3.5:.2f}" text-anchor="end" '
                f'font-family="{self.FF}" font-size="7.5" fill="{self.C_SCALE_T}">'
                f'{round(d, 10):.2f}</text>'
            )
            d = round(d + interval, 10)

        # ── outer box + vertical dividers ─────────────────────────────────────
        for vx in (self.SC_X, self.PF_X, self.ESP_X, self.DESC_X, re):
            parts.append(
                f'<line x1="{vx}" y1="{y0}" x2="{vx}" y2="{yb:.2f}" '
                f'stroke="{self.C_BORDER}" stroke-width="0.8"/>'
            )

        return "\n".join(parts)

    def _legend(self, layers: List[Dict], y0: int) -> Tuple[str, int]:
        seen_sc: List[str] = []
        seen_hex: Dict[str, str] = {}
        for layer in layers:
            sc = layer["sc"]
            if sc not in seen_hex:
                seen_sc.append(sc)
                seen_hex[sc] = layer["hex"]

        if not seen_sc:
            return "", 0

        n_rows   = math.ceil(len(seen_sc) / self.LEG_COLS)
        legend_h = 28 + n_rows * self.LEG_ITEM_H + 14
        re       = self.DESC_X + self.DESC_W
        lx0      = self.SC_X
        col_w    = (re - lx0 - 20) // self.LEG_COLS

        parts = [
            f'<rect x="{lx0}" y="{y0}" width="{re - lx0}" height="{legend_h}" '
            f'fill="{self.C_LEG_BG}" stroke="{self.C_LEG_BD}" stroke-width="0.8"/>',
            f'<text x="{lx0 + 10}" y="{y0 + 17}" font-family="{self.FF}" '
            f'font-size="9.5" font-weight="bold" fill="{self.C_BORDER}">LEYENDA</text>',
            f'<line x1="{lx0 + 10}" y1="{y0 + 21}" x2="{lx0 + 75}" y2="{y0 + 21}" '
            f'stroke="{self.C_BORDER}" stroke-width="0.9"/>',
        ]

        base_y = y0 + 34
        s      = self.LEG_SWATCH
        for i, sc in enumerate(seen_sc):
            col = i % self.LEG_COLS
            row = i // self.LEG_COLS
            ix  = lx0 + 10 + col * col_w
            iy  = base_y + row * self.LEG_ITEM_H
            hx  = "#" + seen_hex[sc]
            parts.append(
                f'<rect x="{ix}" y="{iy}" width="{s}" height="{s}" '
                f'fill="{hx}" stroke="{self.C_BORDER}" stroke-width="0.7"/>'
            )
            parts.append(
                f'<rect x="{ix}" y="{iy}" width="{s}" height="{s}" '
                f'fill="url(#pat_{sc})"/>'
            )
            label = _SOIL_LABELS.get(sc, "Suelo")
            parts.append(
                f'<text x="{ix + s + 6}" y="{iy + s - 3}" '
                f'font-family="{self.FF}" font-size="8.5" fill="{self.C_DESC_T}">'
                f'{_esc(label)}</text>'
            )

        return "\n".join(parts), legend_h

    # ── public API ────────────────────────────────────────────────────────────

    def generate_svg(
        self,
        perforaciones: List[Dict],
        project_name: str = "",
        sondeo: str = "P-1",
        fecha=None,
    ) -> str:
        """Return complete SVG string for the stratigraphic profile."""
        from datetime import date as _date

        if fecha is None:
            fecha_str = _date.today().strftime("%d/%m/%Y")
        elif hasattr(fecha, "strftime"):
            fecha_str = fecha.strftime("%d/%m/%Y")
        else:
            fecha_str = str(fecha)

        layers = self._build_layers(perforaciones)
        if not layers:
            return (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="200">'
                f'<rect width="{self.W}" height="200" fill="white"/>'
                f'<text x="{self.W//2}" y="105" text-anchor="middle" '
                f'font-family="{self.FF}" font-size="13" fill="#888">'
                f'Sin datos de perforaciones</text></svg>'
            )

        total_depth = layers[-1]["d1"]
        ppm         = self._ppm(total_depth)
        used_sc     = {layer["sc"] for layer in layers}

        y_hdr     = 0
        y_col_hdr = self.HEADER_H
        y_profile = self.HEADER_H + self.COL_HDR_H
        profile_h = total_depth * ppm
        y_legend  = int(y_profile + profile_h + self.LEG_MARGIN)

        legend_svg, legend_h = self._legend(layers, y_legend)
        total_h = y_legend + legend_h + 20

        defs_svg = self._defs(
            used_sc,
            self.PF_X, y_profile, self.PF_W, profile_h,
            self.DESC_X, self.DESC_W, total_h,
        )

        return "\n".join([
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.W}" height="{total_h}" '
            f'viewBox="0 0 {self.W} {total_h}">',
            defs_svg,
            f'<rect width="{self.W}" height="{total_h}" fill="white"/>',
            self._header(project_name, sondeo, fecha_str),
            self._col_headers(y_col_hdr),
            self._profile_body(layers, total_depth, ppm, y_profile),
            legend_svg,
            "</svg>",
        ])

    def save_profile(
        self,
        perforaciones: List[Dict],
        output_path: Path,
        project_name: str = "",
        sondeo: str = "P-1",
        fecha=None,
    ) -> Path:
        """Generate SVG and write to *output_path*. No external dependencies."""
        svg = self.generate_svg(perforaciones, project_name, sondeo, fecha)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(svg, encoding="utf-8")
        return output_path

    def save_pdf(
        self,
        perforaciones: List[Dict],
        output_path: Path,
        project_name: str = "",
        sondeo: str = "P-1",
        fecha=None,
    ) -> Path:
        """Export stratigraphic profile as PDF.

        Conversion priority:
        1. *cairosvg* (``pip install cairosvg``) — best fidelity.
        2. *svglib* + *reportlab* (``pip install svglib reportlab``) — pure Python,
           works on Windows with PyInstaller without bundling native DLLs.

        Raises ``RuntimeError`` with install instructions when neither is available.
        """
        svg_bytes = self.generate_svg(perforaciones, project_name, sondeo, fecha).encode("utf-8")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # ── attempt 1: cairosvg ───────────────────────────────────────────────
        try:
            import cairosvg  # type: ignore
            cairosvg.svg2pdf(bytestring=svg_bytes, write_to=str(output_path))
            return output_path
        except ImportError:
            pass

        # ── attempt 2: svglib + reportlab ─────────────────────────────────────
        try:
            import tempfile, os
            from svglib.svglib import svg2rlg         # type: ignore
            from reportlab.graphics import renderPDF  # type: ignore

            with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="wb") as tmp:
                tmp.write(svg_bytes)
                tmp_path = tmp.name
            try:
                drawing = svg2rlg(tmp_path)
                if drawing is None:
                    raise RuntimeError("svglib no pudo leer el SVG generado.")
                renderPDF.drawToFile(drawing, str(output_path))
            finally:
                os.unlink(tmp_path)
            return output_path
        except ImportError:
            pass

        raise RuntimeError(
            "Para exportar PDF instale una de estas librerías:\n"
            "  pip install cairosvg          (requiere Cairo DLLs en Windows)\n"
            "  pip install svglib reportlab  (puro Python, recomendado para Windows)"
        )

    def save_png(
        self,
        perforaciones: List[Dict],
        output_path: Path,
        project_name: str = "",
        sondeo: str = "P-1",
        fecha=None,
        scale: float = 2.0,
    ) -> Path:
        """Export stratigraphic profile as PNG at *scale* ×  resolution.

        Conversion priority:
        1. *cairosvg* — ``pip install cairosvg``
        2. *svglib* + *reportlab* + *Pillow* — ``pip install svglib reportlab Pillow``
        """
        svg_bytes = self.generate_svg(perforaciones, project_name, sondeo, fecha).encode("utf-8")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # ── attempt 1: cairosvg ───────────────────────────────────────────────
        try:
            import cairosvg  # type: ignore
            cairosvg.svg2png(
                bytestring=svg_bytes,
                write_to=str(output_path),
                scale=scale,
            )
            return output_path
        except ImportError:
            pass

        # ── attempt 2: svglib + reportlab + Pillow ────────────────────────────
        try:
            import tempfile, os
            from svglib.svglib import svg2rlg        # type: ignore
            from reportlab.graphics import renderPM  # type: ignore

            with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="wb") as tmp:
                tmp.write(svg_bytes)
                tmp_path = tmp.name
            try:
                drawing = svg2rlg(tmp_path)
                if drawing is None:
                    raise RuntimeError("svglib no pudo leer el SVG generado.")
                drawing.width  *= scale
                drawing.height *= scale
                drawing.transform = (scale, 0, 0, scale, 0, 0)
                renderPM.drawToFile(drawing, str(output_path), fmt="PNG")
            finally:
                os.unlink(tmp_path)
            return output_path
        except ImportError:
            pass

        raise RuntimeError(
            "Para exportar PNG instale una de estas librerías:\n"
            "  pip install cairosvg                       (requiere Cairo DLLs)\n"
            "  pip install svglib reportlab Pillow        (puro Python)"
        )

    # ── convenience dispatcher ────────────────────────────────────────────────

    def save(
        self,
        perforaciones: List[Dict],
        output_path: Path,
        project_name: str = "",
        sondeo: str = "P-1",
        fecha=None,
        **kwargs,
    ) -> Path:
        """Save profile in any supported format, detected from the file extension.

        Supported extensions: ``.svg`` (no deps), ``.pdf``, ``.png``.
        """
        ext = Path(output_path).suffix.lower()
        if ext == ".pdf":
            return self.save_pdf(perforaciones, output_path, project_name, sondeo, fecha)
        if ext == ".png":
            return self.save_png(
                perforaciones, output_path, project_name, sondeo, fecha,
                scale=kwargs.get("scale", 2.0),
            )
        return self.save_profile(perforaciones, output_path, project_name, sondeo, fecha)


# ── module-level singleton (use this in application code) ────────────────────
profile_service = StratigraphicProfileService()


# ── standalone CLI ────────────────────────────────────────────────────────────
# Usage:  python profile_service.py --input datos.json --output perfil.svg
# Works completely offline without the FastAPI web server.

if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        prog="profile_service",
        description="AutoGeo — Generador offline de perfil estratigráfico",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo de archivo JSON de entrada:
  [
    {"profundidad_z": 0.40, "tipo_suelo_principal": "Relleno",
     "color_predominante": "Café oscuro", "descripcion_suelo": "Material heterogéneo"},
    {"profundidad_z": 2.00, "tipo_suelo_principal": "Arcilla",
     "color_predominante": "Café", "descripcion_suelo": "Arcilla de alta plasticidad (CH)"}
  ]
""",
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Archivo JSON con la lista de perforaciones (o ruta a datos del proyecto)",
    )
    parser.add_argument(
        "--output", "-o", default="perfil.svg",
        help="Archivo de salida: .svg (por defecto), .pdf o .png",
    )
    parser.add_argument("--project", "-p", default="", help="Nombre del proyecto")
    parser.add_argument("--sondeo",  "-s", default="P-1", help="Identificador del sondeo")
    parser.add_argument("--fecha",   "-f", default=None,  help="Fecha del estudio (YYYY-MM-DD o DD/MM/YYYY)")
    parser.add_argument("--scale",         default=2.0, type=float,
                        help="Factor de escala para PNG (por defecto 2.0 = doble resolución)")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: no se encontró el archivo '{input_path}'", file=sys.stderr)
        sys.exit(1)

    try:
        raw = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error al leer JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    perfs: List[Dict] = raw if isinstance(raw, list) else raw.get("perforaciones", [])
    if not perfs:
        print("Error: el archivo JSON no contiene perforaciones.", file=sys.stderr)
        sys.exit(1)

    out = Path(args.output)
    try:
        result = profile_service.save(
            perforaciones=perfs,
            output_path=out,
            project_name=args.project,
            sondeo=args.sondeo,
            fecha=args.fecha,
            scale=args.scale,
        )
        print(f"Perfil generado: {result.resolve()}")
    except RuntimeError as exc:
        print(f"Error de exportación:\n{exc}", file=sys.stderr)
        sys.exit(1)
