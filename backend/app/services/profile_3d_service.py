"""
StratigraphicProfile3DService — Sección estratigráfica 3D fotorrealista.

Panel derecho de descripción alineado con las capas (columna Q del Excel de Correlación).
Encabezado profesional con proyecto, sondeo y fecha.
Sin dependencias externas — solo stdlib de Python.
"""
from __future__ import annotations

import math
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

__all__ = ["StratigraphicProfile3DService", "profile_3d_service"]

# ── helpers ────────────────────────────────────────────────────────────────────

def _norm(text: str) -> str:
    nfkd = unicodedata.normalize("NFD", text or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()

def _esc(text: str) -> str:
    return (text or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def _is_dark(hex6: str) -> bool:
    try:
        r,g,b = int(hex6[:2],16), int(hex6[2:4],16), int(hex6[4:],16)
        return (r*299+g*587+b*114)/255000 < 0.52
    except Exception:
        return False

def _lighten(hex6: str, f: float) -> str:
    try:
        ch = [int(hex6[i:i+2],16) for i in (0,2,4)]
        return "".join(f"{min(255,round(c+(255-c)*f)):02X}" for c in ch)
    except Exception:
        return hex6

def _darken(hex6: str, f: float) -> str:
    try:
        ch = [int(hex6[i:i+2],16) for i in (0,2,4)]
        return "".join(f"{max(0,round(c*(1-f))):02X}" for c in ch)
    except Exception:
        return hex6

def _prng(seed: int) -> float:
    seed = ((seed ^ 0xDEADBEEF) + 0x9e3779b9) & 0xFFFFFFFF
    seed = ((seed >> 16) ^ seed) & 0xFFFFFFFF
    seed = (seed * 0x45d9f3b) & 0xFFFFFFFF
    seed = ((seed >> 16) ^ seed) & 0xFFFFFFFF
    return seed / 0xFFFFFFFF

# ── soil classification ────────────────────────────────────────────────────────

_COLOR_MAP: Dict[str,str] = {
    "beige":"F5F0D7","beis":"F5F0D7",
    "cafe":"8B5A2B","cafe oscuro":"5C3D2E","cafe claro":"A0826D",
    "cafe rojizo":"9B6B4A",
    "amarillo":"E8C84A","amarillo claro":"F5E070","amarillo oscuro":"C4A020",
    "amarillo cafe":"9B8C00",
    "rojizo":"C05040","rojo":"BB3B3B","rojo oscuro":"8B1A1A",
    "blanco":"F8F8F8","blanco sucio":"E8E4DC",
    "gris":"808080","gris claro":"C8C8C8","gris oscuro":"484848",
    "gris azuloso":"6A7B8C","gris amarillento":"A8A090",
    "naranja":"D89060","naranja oscuro":"C06020",
    "verde":"7A9C50","verde claro":"A8C87A","verde oscuro":"3A6020",
    "marron":"7A4020","marron claro":"9A7060","marron oscuro":"4A2010",
    "marron rojizo":"8A5040",
    "negro":"282828","negro verdoso":"1B3A2E",
    "crema":"EEE8D0","mostaza":"C8A820","ocre":"B87820",
    "siena":"9A5230","tostado":"C0A878","leonado":"C09830",
    "grisaceo":"909090","pardusco":"7A6848",
    "oscuro":"484848","claro":"DCDCDC",
}

_SOIL_DEFAULTS: Dict[str,str] = {
    "clay":        "C8A060",
    "silt":        "D4B870",
    "fine_sand":   "E8D090",
    "medium_sand": "D8BC60",
    "coarse_sand": "C8A840",
    "gravel":      "B8A880",
    "rock":        "707888",
    "fill":        "B89070",
    "organic":     "342810",
    "unknown":     "C0B090",
}

_SOIL_LABELS: Dict[str,str] = {
    "clay":        "Arcilla",
    "silt":        "Limo",
    "fine_sand":   "Arena fina",
    "medium_sand": "Arena media",
    "coarse_sand": "Arena gruesa",
    "gravel":      "Grava",
    "rock":        "Roca",
    "fill":        "Relleno",
    "organic":     "Mat. orgánico",
    "unknown":     "Suelo",
}

_CLASSIFIERS: List[Tuple[str,str]] = [
    ("arena fina","fine_sand"),("arena media","medium_sand"),
    ("arena gruesa","coarse_sand"),("arena limosa","medium_sand"),
    ("arena arcillosa","medium_sand"),("arena","medium_sand"),
    ("arcillo","clay"),("arcilla","clay"),
    ("limo arcill","silt"),("limo arenos","silt"),("limo","silt"),
    ("gravilla","gravel"),("grava","gravel"),
    ("roca","rock"),("relleno","fill"),
    ("suelo org","organic"),("organico","organic"),
    ("organica","organic"),("turba","organic"),("ceniza","organic"),
    ("vegetal","organic"),
    ("(ch)","clay"),("(cl)","clay"),("(mh)","silt"),("(ml)","silt"),
    ("(sm)","medium_sand"),("(sc)","medium_sand"),
    ("(sp)","coarse_sand"),("(sw)","medium_sand"),
    ("(gm)","gravel"),("(gp)","gravel"),("(gw)","gravel"),
]

def _classify(tipo: Optional[str], desc: Optional[str]=None) -> str:
    for text in (tipo, desc):
        if not text: continue
        n = _norm(text)
        for kw,sc in _CLASSIFIERS:
            if kw in n: return sc
    return "unknown"

def _fill_color(color_name: Optional[str], sc: str) -> str:
    if color_name:
        n = _norm(color_name)
        hit = next((v for k,v in _COLOR_MAP.items() if _norm(k)==n), None)
        if not hit:
            hit = next((v for k,v in _COLOR_MAP.items() if _norm(k) in n or n in _norm(k)), None)
        if hit: return hit
    return _SOIL_DEFAULTS.get(sc, "C0B090")

# ── texture filters ────────────────────────────────────────────────────────────

_TEX: Dict[str,Tuple] = {
    "clay":        ("fractalNoise","0.0010 0.048", 4,  7,  0.52, 0.14),
    "silt":        ("fractalNoise","0.0018 0.038", 3, 11,  0.44, 0.12),
    "fine_sand":   ("turbulence",  "0.070 0.070",  3, 13,  0.56, 0.16),
    "medium_sand": ("turbulence",  "0.048 0.048",  3, 17,  0.58, 0.16),
    "coarse_sand": ("turbulence",  "0.030 0.030",  3, 19,  0.62, 0.18),
    "gravel":      ("turbulence",  "0.016 0.016",  3, 23,  0.65, 0.18),
    "rock":        ("fractalNoise","0.009 0.009",   5, 29,  0.68, 0.20),
    "fill":        ("turbulence",  "0.040 0.040",   2, 31,  0.50, 0.14),
    "organic":     ("fractalNoise","0.006 0.022",   5, 37,  0.60, 0.16),
    "unknown":     ("fractalNoise","0.036 0.036",   3, 53,  0.46, 0.13),
}

def _tex_filter_dark(sc: str) -> str:
    tp,bf,no,seed,_,_ = _TEX.get(sc, ("fractalNoise","0.04",3,53,0.46,0.13))
    return (
        f'<filter id="fdark_{sc}" x="-5%" y="-5%" width="110%" height="110%" '
        f'primitiveUnits="userSpaceOnUse" color-interpolation-filters="linearRGB">'
        f'<feTurbulence type="{tp}" baseFrequency="{bf}" numOctaves="{no}" '
        f'seed="{seed}" result="n"/>'
        f'<feColorMatrix type="luminanceToAlpha" in="n" result="m"/>'
        f'<feFlood flood-color="#1A0A00" result="d"/>'
        f'<feComposite in="d" in2="m" operator="in"/>'
        f'</filter>'
    )

def _tex_filter_light(sc: str) -> str:
    tp,bf,no,seed,_,_ = _TEX.get(sc, ("fractalNoise","0.04",3,53,0.46,0.13))
    seed2 = seed + 71
    parts = bf.split()
    bf2 = " ".join(f"{float(p)*2.2:.4f}" for p in parts)
    return (
        f'<filter id="flight_{sc}" x="-5%" y="-5%" width="110%" height="110%" '
        f'primitiveUnits="userSpaceOnUse" color-interpolation-filters="linearRGB">'
        f'<feTurbulence type="turbulence" baseFrequency="{bf2}" numOctaves="2" '
        f'seed="{seed2}" result="n"/>'
        f'<feColorMatrix type="luminanceToAlpha" in="n" result="m"/>'
        f'<feFlood flood-color="#FFFFFF" result="l"/>'
        f'<feComposite in="l" in2="m" operator="in"/>'
        f'</filter>'
    )

# ── USCS patterns ──────────────────────────────────────────────────────────────

def _pattern(sc: str) -> str:
    d: Dict[str,str] = {
        "clay": (
            f'<pattern id="pat_{sc}" patternUnits="userSpaceOnUse" width="40" height="8">'
            f'<line x1="0" y1="4" x2="40" y2="4" stroke="rgba(0,0,0,0.22)" stroke-width="1.0"/>'
            f'</pattern>'
        ),
        "silt": (
            f'<pattern id="pat_{sc}" patternUnits="userSpaceOnUse" width="16" height="8">'
            f'<line x1="0" y1="4" x2="11" y2="4" stroke="rgba(0,0,0,0.22)" stroke-width="0.9"/>'
            f'</pattern>'
        ),
        "fine_sand": (
            f'<pattern id="pat_{sc}" patternUnits="userSpaceOnUse" width="6" height="6">'
            f'<circle cx="3" cy="3" r="0.8" fill="rgba(0,0,0,0.32)"/>'
            f'</pattern>'
        ),
        "medium_sand": (
            f'<pattern id="pat_{sc}" patternUnits="userSpaceOnUse" width="9" height="9">'
            f'<circle cx="2.5" cy="2.5" r="1.1" fill="rgba(0,0,0,0.30)"/>'
            f'<circle cx="7" cy="7" r="1.1" fill="rgba(0,0,0,0.30)"/>'
            f'</pattern>'
        ),
        "coarse_sand": (
            f'<pattern id="pat_{sc}" patternUnits="userSpaceOnUse" width="11" height="11">'
            f'<circle cx="3" cy="3" r="1.7" fill="rgba(0,0,0,0.27)"/>'
            f'<circle cx="8.5" cy="8.5" r="1.7" fill="rgba(0,0,0,0.27)"/>'
            f'</pattern>'
        ),
        "gravel": (
            f'<pattern id="pat_{sc}" patternUnits="userSpaceOnUse" width="32" height="22">'
            f'<ellipse cx="9" cy="7" rx="7" ry="4.5" fill="none" stroke="rgba(0,0,0,0.42)" stroke-width="1.1"/>'
            f'<ellipse cx="24" cy="15" rx="6" ry="4" fill="none" stroke="rgba(0,0,0,0.40)" stroke-width="1.1"/>'
            f'<ellipse cx="6" cy="19" rx="4.5" ry="2.8" fill="none" stroke="rgba(0,0,0,0.38)" stroke-width="1.0"/>'
            f'</pattern>'
        ),
        "rock": (
            f'<pattern id="pat_{sc}" patternUnits="userSpaceOnUse" width="20" height="20">'
            f'<line x1="0" y1="0" x2="20" y2="20" stroke="rgba(0,0,0,0.36)" stroke-width="1.2"/>'
            f'<line x1="20" y1="0" x2="0" y2="20" stroke="rgba(0,0,0,0.36)" stroke-width="1.2"/>'
            f'</pattern>'
        ),
        "fill": (
            f'<pattern id="pat_{sc}" patternUnits="userSpaceOnUse" width="14" height="14">'
            f'<line x1="0" y1="14" x2="14" y2="0" stroke="rgba(0,0,0,0.30)" stroke-width="1.4"/>'
            f'<line x1="-7" y1="14" x2="7" y2="0" stroke="rgba(0,0,0,0.14)" stroke-width="0.7"/>'
            f'<line x1="7" y1="14" x2="21" y2="0" stroke="rgba(0,0,0,0.14)" stroke-width="0.7"/>'
            f'</pattern>'
        ),
        "organic": (
            f'<pattern id="pat_{sc}" patternUnits="userSpaceOnUse" width="30" height="10">'
            f'<path d="M0,5 Q7.5,1 15,5 Q22.5,9 30,5" fill="none" '
            f'stroke="rgba(255,255,255,0.18)" stroke-width="1.1"/>'
            f'</pattern>'
        ),
        "unknown": (
            f'<pattern id="pat_{sc}" patternUnits="userSpaceOnUse" width="12" height="12">'
            f'<line x1="0" y1="12" x2="12" y2="0" stroke="rgba(0,0,0,0.22)" stroke-width="1.0"/>'
            f'</pattern>'
        ),
    }
    return d.get(sc, d["unknown"])

# ── branching root system ──────────────────────────────────────────────────────

def _root_system(sc: str, x0: float, x1: float, y_top: float, h: float,
                 layer_idx: int) -> List[str]:
    if sc not in ("clay","organic","silt") or h < 20:
        return []
    n_main = 5 if sc == "organic" else 4
    parts: List[str] = []

    def branch(px: float, py: float, angle: float,
               length: float, thick: float, depth: int, rseed: int) -> None:
        if length < 3.5 or depth > 4:
            return
        ex = px + length * math.sin(angle) * 0.75
        ey = py + length * math.cos(angle)
        ey = min(y_top + h - 2, ey)
        ex = max(x0 + 3, min(x1 - 3, ex))
        alpha = min(0.72, 0.38 + thick * 0.095)
        parts.append(
            f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
            f'stroke="rgba(30,12,4,{alpha:.2f})" stroke-width="{thick:.1f}" '
            f'stroke-linecap="round"/>'
        )
        sc_cont  = _prng(rseed * 3 + 1)
        sc_left  = _prng(rseed * 5 + 2)
        sc_right = _prng(rseed * 13 + 5)
        branch(ex, ey, angle + (sc_cont-0.5)*0.42,
               length*0.73, thick*0.73, depth+1, rseed*7+1)
        if sc_left > 0.45:
            branch(ex, ey, angle - 0.55 - _prng(rseed*9+3)*0.38,
                   length*0.58, thick*0.62, depth+1, rseed*11+4)
        if sc_right > 0.60:
            branch(ex, ey, angle + 0.62 + _prng(rseed*17+6)*0.32,
                   length*0.50, thick*0.56, depth+1, rseed*19+7)

    for i in range(n_main):
        s1 = _prng(layer_idx*3000 + i*89 + 11)
        s2 = _prng(layer_idx*3000 + i*89 + 12)
        rx = x0 + 14 + s1*(x1-x0-28)
        rl = min(h*0.62, 28 + s2*22)
        rt = 2.0 + s2*1.4
        ra = (s1-0.5)*0.22
        branch(rx, y_top+3, ra, rl, rt, 0, layer_idx*200+i*23)

    return parts

# ── embedded stones ────────────────────────────────────────────────────────────

def _stones(sc: str, x0: float, x1: float, y_top: float, h: float,
            layer_idx: int) -> List[str]:
    params: Dict[str,Tuple] = {
        "gravel":      (40, 14, 32, 0.55),
        "rock":        (18, 20, 46, 0.60),
        "coarse_sand": (12,  4, 10, 0.70),
    }
    if sc not in params or h < 22: return []
    n, min_r, max_r, mf = params[sc]
    parts: List[str] = []
    placed: List[Tuple] = []

    for j in range(n * 8):
        if len(placed) >= n: break
        s1 = _prng(layer_idx*10000+j*37+1)
        s2 = _prng(layer_idx*10000+j*37+2)
        s3 = _prng(layer_idx*10000+j*37+3)
        s4 = _prng(layer_idx*10000+j*37+4)
        rx  = min_r + s1*(max_r-min_r)
        ry  = rx*(0.52+s2*0.28)
        mx  = rx*mf + 2
        my  = ry*mf + 2
        if (x1-x0) <= 2*mx or h <= 2*my: continue
        cx  = x0 + mx + s3*(x1-x0-2*mx)
        cy  = y_top + my + s4*(h-2*my)
        if any(math.hypot((cx-ox)/(rx+orx), (cy-oy)/(ry+ory)) < 1.02
               for ox,oy,orx,ory in placed):
            continue
        placed.append((cx,cy,rx,ry))
        ang  = s1*60 - 30

        r_dark = int(120 + s2*40);  g_dark = int(105 + s1*35);  b_dark = int(80  + s4*30)
        r_mid  = min(255, r_dark+40); g_mid = min(255, g_dark+35); b_mid = min(255, b_dark+28)
        r_hi   = min(255, r_mid+50);  g_hi  = min(255, g_mid+45);  b_hi  = min(255, b_mid+35)
        r_ol   = max(0, r_dark-55);   g_ol  = max(0, g_dark-48);   b_ol  = max(0, b_dark-38)
        htop = f"{r_hi:02X}{g_hi:02X}{b_hi:02X}"
        hmid = f"{r_mid:02X}{g_mid:02X}{b_mid:02X}"
        hbot = f"{r_dark:02X}{g_dark:02X}{b_dark:02X}"
        outl = f"{r_ol:02X}{g_ol:02X}{b_ol:02X}"
        gid  = f"sg{layer_idx}_{j}"

        parts.append(
            f'<radialGradient id="{gid}" cx="0.30" cy="0.25" r="0.72" '
            f'gradientUnits="objectBoundingBox">'
            f'<stop offset="0%"   stop-color="#{htop}"/>'
            f'<stop offset="45%"  stop-color="#{hmid}"/>'
            f'<stop offset="100%" stop-color="#{hbot}"/>'
            f'</radialGradient>'
        )
        parts.append(
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="url(#{gid})" stroke="#{outl}" stroke-width="1.2" '
            f'transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})"/>'
        )
        hx  = cx - rx*0.26; hy  = cy - ry*0.30
        hrx = rx*0.32;       hry = ry*0.24
        parts.append(
            f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{hrx:.1f}" ry="{hry:.1f}" '
            f'fill="rgba(255,255,255,0.60)" '
            f'transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})"/>'
        )
    return parts

# ── grass surface ──────────────────────────────────────────────────────────────

def _grass_blades(x0: float, x1: float, y_base: float) -> str:
    parts: List[str] = []
    parts.append(
        f'<rect x="{x0}" y="{y_base-6:.1f}" width="{x1-x0}" height="7" '
        f'fill="rgba(12,6,2,0.80)"/>'
    )
    n = max(18, int((x1-x0)/5.5))
    for i in range(n):
        s1 = _prng(i*17+1); s2 = _prng(i*17+2); s3 = _prng(i*17+3); s4 = _prng(i*17+4)
        gx  = x0 + i*(x1-x0)/n + s1*6 - 3
        gh  = 18 + s2*28
        gw  = (s3-0.5)*10
        gcx = gx + gw*0.4
        gcy = y_base - gh*0.55
        gtx = gx + gw
        gty = y_base - gh
        r   = int(14 + s4*30);  g = int(65 + s2*70);  b = int(8 + s1*18)
        rt  = int(30 + s3*40);  gt2 = int(80 + s1*80); bt = int(10 + s2*20)
        sw_base = 1.6 + s1*1.0
        parts.append(
            f'<path d="M{gx:.1f},{y_base:.1f} Q{gcx:.1f},{gcy:.1f} {gtx:.1f},{gty:.1f}" '
            f'fill="none" stroke="rgb({r},{g},{b})" '
            f'stroke-width="{sw_base:.1f}" stroke-linecap="round"/>'
        )
        mid_x = gx + (gtx-gx)*0.55; mid_y = y_base + (gty-y_base)*0.55
        parts.append(
            f'<path d="M{mid_x:.1f},{mid_y:.1f} Q{gcx:.1f},{gcy*0.85:.1f} {gtx:.1f},{gty:.1f}" '
            f'fill="none" stroke="rgb({rt},{gt2},{bt})" '
            f'stroke-width="{sw_base*0.5:.1f}" stroke-linecap="round"/>'
        )
    return "\n".join(parts)

# ── smooth bezier boundaries ───────────────────────────────────────────────────

def _catmull_rom(pts: List[Tuple[float,float]], alpha: float=0.45) -> str:
    if not pts: return ""
    if len(pts) < 2: return f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"
    n = len(pts)
    d = f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"
    for i in range(1,n):
        p0=pts[max(0,i-2)]; p1=pts[i-1]; p2=pts[i]; p3=pts[min(n-1,i+1)]
        cp1x=p1[0]+(p2[0]-p0[0])*alpha/2; cp1y=p1[1]+(p2[1]-p0[1])*alpha/2
        cp2x=p2[0]-(p3[0]-p1[0])*alpha/2; cp2y=p2[1]-(p3[1]-p1[1])*alpha/2
        d += f" C{cp1x:.2f},{cp1y:.2f} {cp2x:.2f},{cp2y:.2f} {p2[0]:.2f},{p2[1]:.2f}"
    return d

def _layer_path(top: List[Tuple[float,float]],
                bot: List[Tuple[float,float]]) -> str:
    top_d = _catmull_rom(top)
    rev   = list(reversed(bot))
    conn  = f" L{rev[0][0]:.2f},{rev[0][1]:.2f}"
    n     = len(rev); a = 0.45; segs: List[str] = []
    for i in range(1,n):
        p0=rev[max(0,i-2)]; p1=rev[i-1]; p2=rev[i]; p3=rev[min(n-1,i+1)]
        cp1x=p1[0]+(p2[0]-p0[0])*a/2; cp1y=p1[1]+(p2[1]-p0[1])*a/2
        cp2x=p2[0]-(p3[0]-p1[0])*a/2; cp2y=p2[1]-(p3[1]-p1[1])*a/2
        segs.append(f"C{cp1x:.2f},{cp1y:.2f} {cp2x:.2f},{cp2y:.2f} {p2[0]:.2f},{p2[1]:.2f}")
    return top_d + conn + " " + " ".join(segs) + " Z"

_AMPLITUDE: Dict[str,float] = {
    "clay":2.5,"silt":2.0,"fine_sand":1.2,"medium_sand":1.0,
    "coarse_sand":2.5,"gravel":3.5,"rock":5.0,
    "fill":3.0,"organic":5.0,"unknown":2.5,
}

def _boundary_pts(x0: float, x1: float, y: float,
                  amplitude: float, seed: int, n: int=16
                  ) -> List[Tuple[float,float]]:
    pts: List[Tuple[float,float]] = [(x0, y)]
    for i in range(1, n):
        t  = i/n; x = x0+(x1-x0)*t
        dy = (amplitude*0.58*math.sin(seed*3.7+t*math.pi*2.4) +
              amplitude*0.42*math.sin(seed*1.3+t*math.pi*5.1))
        pts.append((round(x,2), round(y+dy,2)))
    pts.append((x1,y))
    return pts

# ── word-wrap helper ───────────────────────────────────────────────────────────

def _wrap_text(text: str, max_chars: int) -> List[str]:
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

# ── main service ───────────────────────────────────────────────────────────────

class StratigraphicProfile3DService:
    """
    Perfil estratigráfico 3D fotorrealista con panel descriptivo (columna Q).
    Completamente offline — solo stdlib de Python para la generación SVG.
    """

    W        = 820      # ancho total del canvas
    HEADER_H = 55       # altura del encabezado
    SEC_X    = 72       # borde izquierdo del perfil 3D
    SEC_W    = 388      # ancho del cuerpo del perfil
    EXT_DX   = 52       # profundidad de extrusión 3D
    EXT_DY   = 26       # altura de extrusión 3D
    LEGEND_X = 532      # borde izquierdo del panel de descripción
    LEGEND_W = 276      # ancho del panel de descripción
    Y0       = 145      # y donde empiezan las capas del perfil
    FF       = "Arial, Helvetica, sans-serif"

    def _ppm(self, depth: float) -> float:
        return max(500.0, min(1200.0, 110.0*depth)) / depth

    def _interval(self, depth: float) -> float:
        if depth <= 3.0:  return 0.25
        if depth <= 8.0:  return 0.5
        if depth <= 20.0: return 1.0
        return 2.0

    def _build_layers(self, perf: List[Dict]) -> List[Dict]:
        layers: List[Dict] = []
        prev = 0.0
        for item in (perf or []):
            try:
                end = float(str(item.get("profundidad_z") or 0).replace(",","."))
            except Exception:
                end = prev+1.0
            if end <= prev: end = prev+0.5
            tipo  = str(item.get("tipo_suelo_principal") or "").strip()
            desc  = str(item.get("descripcion_suelo")    or tipo).strip()
            color = str(item.get("color_predominante")   or "").strip()
            sc    = _classify(tipo, desc)
            hex6  = _fill_color(color, sc)
            layers.append({
                "d0":   prev,
                "d1":   end,
                "esp":  round(end-prev, 3),
                "sc":   sc,
                "hex":  hex6,
                "label": _SOIL_LABELS.get(sc, "Suelo"),
                "desc":  desc or _SOIL_LABELS.get(sc, "Suelo"),
            })
            prev = end
        return layers

    def _header(self, project_name: str, sondeo: str, fecha: str) -> str:
        w  = self.W
        h1 = 36
        h2 = self.HEADER_H - h1
        proj = _esc((project_name or "")[:90])
        return "\n".join([
            # Barra de título
            f'<defs>'
            f'<linearGradient id="gHdr" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="#1C3A5C"/>'
            f'<stop offset="100%" stop-color="#0D2540"/>'
            f'</linearGradient></defs>',
            f'<rect x="0" y="0" width="{w}" height="{h1}" fill="url(#gHdr)"/>',
            # Línea decorativa izquierda
            f'<rect x="0" y="0" width="5" height="{h1}" fill="#4A90D9"/>',
            f'<text x="{w//2}" y="24" text-anchor="middle" font-family="{self.FF}" '
            f'font-size="15" font-weight="bold" letter-spacing="2" fill="#FFFFFF" '
            f'filter="url(#gTS)">PERFIL ESTRATIGRÁFICO 3D DEL SUELO</text>',
            # Barra de información
            f'<rect x="0" y="{h1}" width="{w}" height="{h2}" fill="#2D5E8C"/>',
            f'<text x="14" y="{h1+13}" font-family="{self.FF}" font-size="7.5" fill="#D0E4FF">'
            f'<tspan font-weight="bold" fill="#FFFFFF">PROYECTO: </tspan>{proj}</text>',
            f'<text x="{w//2}" y="{h1+13}" text-anchor="middle" font-family="{self.FF}" '
            f'font-size="7.5" fill="#D0E4FF">'
            f'<tspan font-weight="bold" fill="#FFFFFF">SONDEO: </tspan>{_esc(sondeo)}</text>',
            f'<text x="{w-14}" y="{h1+13}" text-anchor="end" font-family="{self.FF}" '
            f'font-size="7.5" fill="#D0E4FF">'
            f'<tspan font-weight="bold" fill="#FFFFFF">FECHA: </tspan>{_esc(fecha)}</text>',
            # Línea separadora
            f'<line x1="0" y1="{self.HEADER_H}" x2="{w}" y2="{self.HEADER_H}" '
            f'stroke="#4A90D9" stroke-width="1.5"/>',
        ])

    def _legend_panel(self, layers: List[Dict], ppm: float, total_h: int) -> str:
        lx  = self.LEGEND_X
        lw  = self.LEGEND_W
        parts: List[str] = []

        panel_bottom = total_h - 8
        panel_top    = self.Y0 - 24  # comienza justo sobre las capas (espacio para título)

        # Fondo del panel
        parts.append(
            f'<rect x="{lx}" y="{panel_top}" width="{lw}" '
            f'height="{panel_bottom - panel_top}" '
            f'fill="#F8F7F5" stroke="#C0C0C0" stroke-width="1.0" rx="4"/>'
        )

        # Barra de título del panel
        parts.append(
            f'<rect x="{lx}" y="{panel_top}" width="{lw}" height="22" '
            f'fill="#1C3A5C" rx="4"/>'
        )
        parts.append(
            f'<rect x="{lx}" y="{panel_top+10}" width="{lw}" height="12" fill="#1C3A5C"/>'
        )
        parts.append(
            f'<text x="{lx + lw//2}" y="{panel_top + 15}" text-anchor="middle" '
            f'font-family="{self.FF}" font-size="8.5" font-weight="bold" fill="#FFFFFF">'
            f'DESCRIPCIÓN ESTRATIGRÁFICA</text>'
        )

        # Cada capa alineada con el perfil 3D
        for i, lay in enumerate(layers):
            ly_start = self.Y0 + lay["d0"] * ppm
            ly_h     = max(28.0, lay["esp"] * ppm)
            hex6     = lay["hex"]

            # Fondo alterno
            row_bg = "#F2F0EE" if i % 2 == 0 else "#E8E6E4"
            parts.append(
                f'<rect x="{lx+1}" y="{ly_start:.1f}" width="{lw-2}" '
                f'height="{ly_h:.1f}" fill="{row_bg}"/>'
            )

            # Swatch de color con patrón
            sw_h = max(10.0, min(ly_h - 10, 44.0))
            parts.append(
                f'<rect x="{lx+5}" y="{ly_start+5:.1f}" width="15" '
                f'height="{sw_h:.1f}" fill="#{hex6}" '
                f'stroke="rgba(0,0,0,0.35)" stroke-width="0.8" rx="2"/>'
            )
            parts.append(
                f'<rect x="{lx+5}" y="{ly_start+5:.1f}" width="15" '
                f'height="{sw_h:.1f}" fill="url(#pat_{lay["sc"]})" '
                f'rx="2" opacity="0.6"/>'
            )

            # Rango de profundidad (negrita, azul oscuro)
            parts.append(
                f'<text x="{lx+25}" y="{ly_start+14:.1f}" '
                f'font-family="{self.FF}" font-size="7.5" font-weight="bold" fill="#1C3A5C">'
                f'{lay["d0"]:.2f} – {lay["d1"]:.2f} m'
                f'<tspan fill="#888" font-weight="normal">  ({lay["esp"]:.2f} m)</tspan>'
                f'</text>'
            )

            # Tipo de suelo en cursiva
            parts.append(
                f'<text x="{lx+25}" y="{ly_start+24:.1f}" '
                f'font-family="{self.FF}" font-size="7" fill="#5A6A7A" '
                f'font-style="italic">{_esc(lay["label"])}</text>'
            )

            # Descripción macroscópica (columna Q) — con word-wrap
            if ly_h > 30:
                desc_text  = lay.get("desc") or lay["label"]
                max_chars  = max(20, int((lw - 34) / 4.3))
                lines_txt  = _wrap_text(desc_text, max_chars)
                avail_h    = ly_h - 30
                max_lines  = max(1, int(avail_h / 9.5))
                for j, ln_text in enumerate(lines_txt[:max_lines]):
                    ty = ly_start + 33 + j * 9.5
                    parts.append(
                        f'<text x="{lx+25}" y="{ty:.1f}" '
                        f'font-family="{self.FF}" font-size="7" fill="#333">'
                        f'{_esc(ln_text)}</text>'
                    )
                if len(lines_txt) > max_lines:
                    ey = ly_start + 33 + (max_lines - 1) * 9.5
                    parts.append(
                        f'<text x="{lx+lw-7}" y="{ey:.1f}" text-anchor="end" '
                        f'font-family="{self.FF}" font-size="7" fill="#AAA">…</text>'
                    )

            # Divisor entre capas
            parts.append(
                f'<line x1="{lx+1}" y1="{ly_start+ly_h:.1f}" '
                f'x2="{lx+lw-1}" y2="{ly_start+ly_h:.1f}" '
                f'stroke="#CCCCCC" stroke-width="0.5"/>'
            )

        return "\n".join(parts)

    def _defs(self, layers: List[Dict], boundaries: List[List[Tuple[float,float]]],
              ppm: float, defs_extra: List[str]) -> str:
        used = {l["sc"] for l in layers}
        P: List[str] = ["<defs>"]

        for sc in used:
            P.append(f"  {_tex_filter_dark(sc)}")
            P.append(f"  {_tex_filter_light(sc)}")

        for sc in used:
            P.append(f"  {_pattern(sc)}")

        for i,_ in enumerate(layers):
            path = _layer_path(boundaries[i], boundaries[i+1])
            P.append(f'  <clipPath id="cpl{i}"><path d="{path}"/></clipPath>')

        for i,lay in enumerate(layers):
            h6  = lay["hex"]
            ys  = self.Y0 + lay["d0"]*ppm
            he  = lay["esp"]*ppm
            ct  = _lighten(h6, 0.42)
            cm  = _lighten(h6, 0.12)
            cb  = _darken(h6, 0.32)
            P.append(
                f'  <linearGradient id="gL{i}" x1="0" y1="{ys:.1f}" '
                f'x2="0" y2="{ys+he:.1f}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0%"   stop-color="#{ct}"/>'
                f'<stop offset="20%"  stop-color="#{cm}"/>'
                f'<stop offset="70%"  stop-color="#{h6}"/>'
                f'<stop offset="100%" stop-color="#{cb}"/>'
                f'</linearGradient>'
            )
            cr0 = _darken(h6, 0.50)
            cr1 = _darken(h6, 0.68)
            P.append(
                f'  <linearGradient id="gR{i}" x1="0" y1="{ys:.1f}" '
                f'x2="0" y2="{ys+he:.1f}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0%"   stop-color="#{cr0}"/>'
                f'<stop offset="100%" stop-color="#{cr1}"/>'
                f'</linearGradient>'
            )

        if layers:
            ct  = _lighten(layers[0]["hex"], 0.62)
            ct2 = _lighten(layers[0]["hex"], 0.32)
            P.append(
                f'  <linearGradient id="gTop" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0%"   stop-color="#{ct}"/>'
                f'<stop offset="100%" stop-color="#{ct2}"/>'
                f'</linearGradient>'
            )

        P.append(
            '  <linearGradient id="gSpec" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%"   stop-color="#FFF" stop-opacity="0.46"/>'
            '<stop offset="22%"  stop-color="#FFF" stop-opacity="0.0"/>'
            '</linearGradient>'
        )
        P.append(
            '  <linearGradient id="gAO" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0%"   stop-color="#000" stop-opacity="0.0"/>'
            '<stop offset="100%" stop-color="#000" stop-opacity="0.38"/>'
            '</linearGradient>'
        )
        P.append(
            '  <linearGradient id="gEdge" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0%"   stop-color="#FFF" stop-opacity="0.28"/>'
            '<stop offset="10%"  stop-color="#FFF" stop-opacity="0.0"/>'
            '</linearGradient>'
        )
        P.append(
            '  <filter id="gShd" x="-8%" y="-4%" width="125%" height="118%">'
            '<feGaussianBlur in="SourceAlpha" stdDeviation="9" result="b"/>'
            '<feOffset dx="8" dy="12" result="o"/>'
            '<feFlood flood-color="rgba(0,0,0,0.35)" result="c"/>'
            '<feComposite in="c" in2="o" operator="in" result="s"/>'
            '<feBlend in="SourceGraphic" in2="s" mode="normal"/>'
            '</filter>'
        )
        P.append(
            '  <filter id="gTS">'
            '<feGaussianBlur in="SourceAlpha" stdDeviation="1.5" result="b"/>'
            '<feOffset dx="1" dy="1" result="o"/>'
            '<feFlood flood-color="rgba(0,0,0,0.70)" result="c"/>'
            '<feComposite in="c" in2="o" operator="in" result="s"/>'
            '<feBlend in="SourceGraphic" in2="s" mode="normal"/>'
            '</filter>'
        )

        for d in defs_extra:
            P.append(f"  {d}")

        P.append("</defs>")
        return "\n".join(P)

    def _top_cap(self, top_pts: List[Tuple[float,float]]) -> str:
        x0,x1 = self.SEC_X, self.SEC_X+self.SEC_W
        dx,dy  = self.EXT_DX, self.EXT_DY
        y      = top_pts[0][1]
        pts    = (f"{x0},{y:.1f} {x1},{y:.1f} "
                  f"{x1+dx},{y-dy:.1f} {x0+dx},{y-dy:.1f}")
        return (
            f'<polygon points="{pts}" fill="#C8BC98" '
            f'stroke="rgba(0,0,0,0.60)" stroke-width="1.0"/>'
            f'<polygon points="{pts}" fill="url(#gTop)" opacity="0.82"/>'
        )

    def _draw_layer(self, lay: Dict, idx: int,
                    top_pts: List[Tuple[float,float]],
                    bot_pts: List[Tuple[float,float]],
                    ppm: float, is_last: bool,
                    defs_extra: List[str]) -> str:
        sc   = lay["sc"]
        hex6 = lay["hex"]
        ys   = self.Y0+lay["d0"]*ppm
        he   = lay["esp"]*ppm
        x0   = self.SEC_X
        x1   = self.SEC_X+self.SEC_W
        _,_,_,_,dark_op,light_op = _TEX.get(sc, ("","","",0,0.46,0.13))
        P: List[str] = []

        P.append(
            f'<rect x="{x0}" y="{ys:.1f}" width="{self.SEC_W}" height="{he:.1f}" '
            f'fill="url(#gL{idx})" clip-path="url(#cpl{idx})"/>'
        )
        if he > 10:
            P.append(
                f'<rect x="{x0}" y="{ys:.1f}" width="{self.SEC_W}" height="{he:.1f}" '
                f'filter="url(#fdark_{sc})" clip-path="url(#cpl{idx})" '
                f'opacity="{dark_op:.2f}"/>'
            )
        if he > 10:
            P.append(
                f'<rect x="{x0}" y="{ys:.1f}" width="{self.SEC_W}" height="{he:.1f}" '
                f'filter="url(#flight_{sc})" clip-path="url(#cpl{idx})" '
                f'opacity="{light_op:.2f}"/>'
            )

        pat_op = 0.0 if sc in ("gravel","rock","coarse_sand") else 0.48
        if he > 14 and pat_op > 0:
            P.append(
                f'<rect x="{x0}" y="{ys:.1f}" width="{self.SEC_W}" height="{he:.1f}" '
                f'fill="url(#pat_{sc})" clip-path="url(#cpl{idx})" opacity="{pat_op:.2f}"/>'
            )

        for root_el in _root_system(sc, x0, x1, ys, he, idx):
            P.append(root_el)

        for s in _stones(sc, x0+14, x1-14, ys+7, he-14, idx):
            if s.startswith('<radialGradient'):
                defs_extra.append(s)
            else:
                P.append(s)

        if he > 10:
            strip = min(he*0.25, 20)
            P.append(
                f'<rect x="{x0}" y="{ys:.1f}" width="{self.SEC_W}" height="{strip:.1f}" '
                f'fill="url(#gSpec)" clip-path="url(#cpl{idx})"/>'
            )
        if he > 10:
            ew = min(self.SEC_W*0.10, 32)
            P.append(
                f'<rect x="{x0}" y="{ys:.1f}" width="{ew:.1f}" height="{he:.1f}" '
                f'fill="url(#gEdge)" clip-path="url(#cpl{idx})"/>'
            )
        if he > 28:
            ao_h = min(he*0.24, 22)
            P.append(
                f'<rect x="{x0}" y="{ys+he-ao_h:.1f}" width="{self.SEC_W}" '
                f'height="{ao_h:.1f}" fill="url(#gAO)" clip-path="url(#cpl{idx})"/>'
            )

        path = _layer_path(top_pts, bot_pts)
        edge = f"#{_darken(hex6, 0.54)}"
        P.append(f'<path d="{path}" fill="none" stroke="{edge}" stroke-width="0.9"/>')

        # Cara de extrusión derecha
        rty = top_pts[-1][1]; rby = bot_pts[-1][1]
        ext = (f"{x1},{rty:.1f} {x1+self.EXT_DX},{rty-self.EXT_DY:.1f} "
               f"{x1+self.EXT_DX},{rby-self.EXT_DY:.1f} {x1},{rby:.1f}")
        P.append(
            f'<polygon points="{ext}" fill="url(#gR{idx})" '
            f'stroke="{edge}" stroke-width="0.8" stroke-linejoin="round"/>'
        )
        P.append(
            f'<line x1="{x1}" y1="{rty:.1f}" x2="{x1}" y2="{rby:.1f}" '
            f'stroke="rgba(255,255,255,0.55)" stroke-width="1.8"/>'
        )

        # Etiqueta dentro de la capa
        fg = "#FFFFFF" if _is_dark(hex6) else "#1A1A1A"
        cx = x0+self.SEC_W/2; cy = ys+he/2
        if he > 32:
            P.append(
                f'<text x="{cx:.1f}" y="{cy+4:.1f}" text-anchor="middle" '
                f'font-family="{self.FF}" font-size="11.5" font-weight="bold" '
                f'font-style="italic" fill="{fg}" filter="url(#gTS)">'
                f'{_esc(lay["label"])}</text>'
            )
        if he > 62:
            P.append(
                f'<text x="{cx:.1f}" y="{cy+20:.1f}" text-anchor="middle" '
                f'font-family="{self.FF}" font-size="9.5" fill="{fg}" opacity="0.80">'
                f'{lay["d0"]:.2f} – {lay["d1"]:.2f} m</text>'
            )
        return "\n".join(P)

    def _scale(self, total_depth: float, ppm: float) -> str:
        iv  = self._interval(total_depth)
        sx  = self.SEC_X - 10
        bot = self.Y0+total_depth*ppm
        P: List[str] = [
            f'<line x1="{sx}" y1="{self.Y0:.1f}" x2="{sx}" y2="{bot:.1f}" '
            f'stroke="#444" stroke-width="1.5"/>',
        ]
        d = 0.0
        while d <= total_depth+1e-9:
            sy = self.Y0+d*ppm
            P.append(f'<line x1="{sx-8}" y1="{sy:.1f}" x2="{sx}" y2="{sy:.1f}" '
                     f'stroke="#444" stroke-width="1.5"/>')
            P.append(f'<text x="{sx-11}" y="{sy+3.5:.1f}" text-anchor="end" '
                     f'font-family="{self.FF}" font-size="10" fill="#333">'
                     f'{round(d,6):.2f}</text>')
            d = round(d+iv,10)
        d2 = iv/2.0; d = d2
        while d <= total_depth+1e-9:
            if abs((d/iv)-round(d/iv)) > 1e-9:
                sy = self.Y0+d*ppm
                P.append(f'<line x1="{sx-4}" y1="{sy:.1f}" x2="{sx}" y2="{sy:.1f}" '
                         f'stroke="#888" stroke-width="0.9"/>')
            d = round(d+d2,10)
        mid = self.Y0+total_depth*ppm/2
        P.append(
            f'<text x="{sx-28}" y="{mid:.1f}" text-anchor="middle" '
            f'font-family="{self.FF}" font-size="9.5" fill="#555" '
            f'transform="rotate(-90 {sx-28} {mid:.1f})">Profundidad (m)</text>'
        )
        return "\n".join(P)

    def generate_svg(
        self,
        perforaciones: List[Dict],
        project_name:  str = "",
        sondeo:        str = "P-1",
        fecha               = None,
    ) -> str:
        from datetime import date as _date_cls
        if fecha is None:
            fecha_str = _date_cls.today().strftime("%d/%m/%Y")
        elif hasattr(fecha, "strftime"):
            fecha_str = fecha.strftime("%d/%m/%Y")
        else:
            fecha_str = str(fecha)

        layers = self._build_layers(perforaciones)
        if not layers:
            return (
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="200">'
                f'<rect width="{self.W}" height="200" fill="#F0EDE8"/>'
                f'<text x="{self.W//2}" y="105" text-anchor="middle" '
                f'font-family="{self.FF}" font-size="13" fill="#888">'
                f'Sin datos</text></svg>'
            )

        total_d = layers[-1]["d1"]
        ppm     = self._ppm(total_d)
        prof_h  = total_d*ppm
        x0      = self.SEC_X
        x1      = self.SEC_X+self.SEC_W

        boundaries: List[List[Tuple[float,float]]] = []
        for i,lay in enumerate(layers):
            y_top = self.Y0+lay["d0"]*ppm
            amp   = 0.0 if i==0 else _AMPLITUDE.get(layers[i-1]["sc"],4.5)*0.78
            boundaries.append(_boundary_pts(x0, x1, y_top, amp, i))
        boundaries.append(_boundary_pts(x0, x1, self.Y0+total_d*ppm, 0.0, len(layers)))

        defs_extra: List[str] = []
        layer_svgs: List[str] = []
        for i,lay in enumerate(layers):
            layer_svgs.append(
                self._draw_layer(lay, i, boundaries[i], boundaries[i+1],
                                 ppm, i==len(layers)-1, defs_extra)
            )

        total_h  = int(self.Y0+prof_h+40)
        defs_svg = self._defs(layers, boundaries, ppm, defs_extra)

        border = "\n".join([
            f'<line x1="{x0}" y1="{self.Y0:.1f}" x2="{x0}" '
            f'y2="{self.Y0+prof_h:.1f}" stroke="#222" stroke-width="1.8"/>',
            f'<line x1="{x0}" y1="{self.Y0+prof_h:.1f}" x2="{x1}" '
            f'y2="{self.Y0+prof_h:.1f}" stroke="#222" stroke-width="1.1"/>',
        ])
        ext_edges = "\n".join([
            f'<line x1="{x1+self.EXT_DX}" y1="{self.Y0-self.EXT_DY:.1f}" '
            f'x2="{x1+self.EXT_DX}" y2="{self.Y0+prof_h-self.EXT_DY:.1f}" '
            f'stroke="#555" stroke-width="1.0"/>',
            f'<line x1="{x1}" y1="{self.Y0+prof_h:.1f}" '
            f'x2="{x1+self.EXT_DX}" y2="{self.Y0+prof_h-self.EXT_DY:.1f}" '
            f'stroke="#555" stroke-width="1.0"/>',
        ])

        # Pasto siempre visible en la superficie
        grass_svg = _grass_blades(x0, x1, self.Y0 - 2)

        # Franja de suelo superficial
        ground_strip = (
            f'<rect x="{x0}" y="{self.Y0-2}" width="{self.SEC_W}" height="3" '
            f'fill="rgba(40,20,5,0.60)"/>'
        )

        header_svg   = self._header(project_name, sondeo, fecha_str)
        legend_svg   = self._legend_panel(layers, ppm, total_h)

        # Nota inferior
        footer = (
            f'<text x="{x0}" y="{total_h - 6}" font-family="{self.FF}" '
            f'font-size="7" fill="#999">AutoGeo — Perfil estratigráfico generado automáticamente</text>'
        )

        return "\n".join([
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.W}" height="{total_h}" '
            f'viewBox="0 0 {self.W} {total_h}">',
            defs_svg,
            f'<rect width="{self.W}" height="{total_h}" fill="#EDEAE4"/>',
            header_svg,
            '<g filter="url(#gShd)">',
            self._top_cap(boundaries[0]),
            "\n".join(layer_svgs),
            '</g>',
            border,
            ext_edges,
            ground_strip,
            grass_svg,
            self._scale(total_d, ppm),
            legend_svg,
            footer,
            "</svg>",
        ])

    def save_profile_3d(
        self,
        perforaciones: List[Dict],
        output_path:   Path,
        project_name:  str = "",
        sondeo:        str = "P-1",
        fecha               = None,
    ) -> Path:
        svg = self.generate_svg(perforaciones, project_name, sondeo, fecha)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(svg, encoding="utf-8")
        return output_path


profile_3d_service = StratigraphicProfile3DService()
