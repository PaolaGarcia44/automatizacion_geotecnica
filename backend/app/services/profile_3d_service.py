"""
StratigraphicProfile3DService — Perfil 3D con texturas estilo AutoCAD (USCS).

Patrones geométricos limpios: líneas de arcilla, puntos de arena, elipses de grava,
cruces de roca. Sin filtros de ruido — aspecto técnico-geológico profesional.
100% offline, solo stdlib de Python.
"""
from __future__ import annotations

import math
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.core.constants import COLOR_MAP as _COLOR_MAP

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
        return (r*299+g*587+b*114)/255000 < 0.50
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

# ── clasificación de suelos ────────────────────────────────────────────────────
# _COLOR_MAP importado desde constants.py — fuente única de verdad compartida
# con excel_service.  Las claves ya están normalizadas (sin tildes, minúsculas).

# Colores base claros → los patrones oscuros se verán como en AutoCAD
_SOIL_DEFAULTS: Dict[str,str] = {
    "clay":        "D8B888",   # arcilla: beige cálido
    "silt":        "CCC0A0",   # limo: gris-beige
    "fine_sand":   "E8D898",   # arena fina: crema dorada
    "medium_sand": "DECA80",   # arena media: dorado suave
    "coarse_sand": "CEB868",   # arena gruesa: dorado terroso
    "gravel":      "BEB898",   # grava: gris cálido
    "rock":        "9898A8",   # roca: gris medio-azulado
    "fill":        "C0AE98",   # relleno: café grisáceo
    "organic":     "281408",   # orgánico: marrón muy oscuro
    "unknown":     "CCC0A8",   # desconocido: beige neutral
}

_SOIL_LABELS: Dict[str,str] = {
    "clay":"Arcilla","silt":"Limo","fine_sand":"Arena fina",
    "medium_sand":"Arena media","coarse_sand":"Arena gruesa",
    "gravel":"Grava","rock":"Roca","fill":"Relleno",
    "organic":"Mat. orgánico","unknown":"Suelo",
}

_CLASSIFIERS: List[Tuple[str,str]] = [
    ("arena fina","fine_sand"),("arena media","medium_sand"),
    ("arena gruesa","coarse_sand"),("arena limosa","medium_sand"),
    ("arena arcillosa","medium_sand"),("arena","medium_sand"),
    ("arcillo","clay"),("arcilla","clay"),
    ("limo arcill","silt"),("limo arenos","silt"),("limo","silt"),
    ("gravilla","gravel"),("grava","gravel"),
    ("roca","rock"),("relleno","fill"),
    ("suelo org","organic"),("organico","organic"),("organica","organic"),
    ("turba","organic"),("ceniza","organic"),("vegetal","organic"),
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
        if hit:
            # aclaramos el color para que los patrones sean visibles sobre él
            return _lighten(hit, 0.28)
    return _SOIL_DEFAULTS.get(sc, "CCC0A8")

# ── patrones USCS estilo AutoCAD ───────────────────────────────────────────────
# Todos usan trazos negros/oscuros nítidos sobre el color de fondo.
# Opacidad del patrón: 0.82-0.90 para máxima visibilidad.

def _pattern(sc: str) -> str:
    """Patrones SVG USCS — aspecto técnico-geológico profesional."""
    d: Dict[str,str] = {

        # Arcilla (CL/CH): reticulado diagonal cruzado (depósito arcilloso)
        "clay": (
            '<pattern id="pat_clay" patternUnits="userSpaceOnUse" width="18" height="18">'
            '<line x1="0" y1="0" x2="18" y2="18" stroke="rgba(0,0,0,0.60)" stroke-width="1.1"/>'
            '<line x1="18" y1="0" x2="0" y2="18" stroke="rgba(0,0,0,0.60)" stroke-width="1.1"/>'
            '</pattern>'
        ),

        # Limo (ML/MH): guiones horizontales alternados con línea naranja de acento
        "silt": (
            '<pattern id="pat_silt" patternUnits="userSpaceOnUse" width="30" height="10">'
            '<line x1="0"  y1="2.5" x2="12" y2="2.5"'
            ' stroke="rgba(0,0,0,0.52)" stroke-width="0.9" stroke-linecap="round"/>'
            '<line x1="15" y1="2.5" x2="26" y2="2.5"'
            ' stroke="rgba(0,0,0,0.52)" stroke-width="0.9" stroke-linecap="round"/>'
            '<line x1="0"  y1="6.0" x2="30" y2="6.0"'
            ' stroke="rgba(205,95,15,0.72)" stroke-width="1.0"/>'
            '<line x1="2"  y1="9.0" x2="11" y2="9.0"'
            ' stroke="rgba(0,0,0,0.38)" stroke-width="0.7" stroke-linecap="round"/>'
            '<line x1="14" y1="9.0" x2="23" y2="9.0"'
            ' stroke="rgba(0,0,0,0.38)" stroke-width="0.7" stroke-linecap="round"/>'
            '</pattern>'
        ),

        # Arena fina: puntos pequeños en cuadrícula offset
        "fine_sand": (
            '<pattern id="pat_fine_sand" patternUnits="userSpaceOnUse" width="8" height="8">'
            '<circle cx="2" cy="2" r="0.95" fill="rgba(0,0,0,0.60)"/>'
            '<circle cx="6" cy="6" r="0.95" fill="rgba(0,0,0,0.60)"/>'
            '<circle cx="6" cy="2" r="0.65" fill="rgba(0,0,0,0.36)"/>'
            '<circle cx="2" cy="6" r="0.65" fill="rgba(0,0,0,0.36)"/>'
            '</pattern>'
        ),

        # Arena media: puntos medianos en grid desplazado
        "medium_sand": (
            '<pattern id="pat_medium_sand" patternUnits="userSpaceOnUse" width="10" height="10">'
            '<circle cx="2" cy="2" r="1.45" fill="rgba(0,0,0,0.58)"/>'
            '<circle cx="7" cy="7" r="1.45" fill="rgba(0,0,0,0.58)"/>'
            '<circle cx="7" cy="2" r="1.0"  fill="rgba(0,0,0,0.38)"/>'
            '<circle cx="2" cy="7" r="1.0"  fill="rgba(0,0,0,0.38)"/>'
            '</pattern>'
        ),

        # Arena gruesa: puntos grandes con variación de tamaño
        "coarse_sand": (
            '<pattern id="pat_coarse_sand" patternUnits="userSpaceOnUse" width="13" height="13">'
            '<circle cx="3"   cy="3"   r="1.9"  fill="rgba(0,0,0,0.56)"/>'
            '<circle cx="9.5" cy="9.5" r="1.9"  fill="rgba(0,0,0,0.56)"/>'
            '<circle cx="9.5" cy="3"   r="1.35" fill="rgba(0,0,0,0.38)"/>'
            '<circle cx="3"   cy="9.5" r="1.35" fill="rgba(0,0,0,0.38)"/>'
            '<circle cx="6.5" cy="6.5" r="0.75" fill="rgba(0,0,0,0.24)"/>'
            '</pattern>'
        ),

        # Grava (GW/GP): cantos redondeados con leve relleno
        "gravel": (
            '<pattern id="pat_gravel" patternUnits="userSpaceOnUse" width="40" height="26">'
            '<ellipse cx="11" cy="8"  rx="9"   ry="5.5"'
            ' fill="rgba(0,0,0,0.06)" stroke="rgba(0,0,0,0.68)" stroke-width="1.3"/>'
            '<ellipse cx="30" cy="18" rx="8"   ry="4.5"'
            ' fill="rgba(0,0,0,0.05)" stroke="rgba(0,0,0,0.62)" stroke-width="1.2"/>'
            '<ellipse cx="6"  cy="21" rx="5"   ry="3"'
            ' fill="rgba(0,0,0,0.04)" stroke="rgba(0,0,0,0.56)" stroke-width="1.0"/>'
            '<ellipse cx="34" cy="5"  rx="5.5" ry="3"'
            ' fill="rgba(0,0,0,0.04)" stroke="rgba(0,0,0,0.52)" stroke-width="1.0"/>'
            '</pattern>'
        ),

        # Roca (BR): reticulado diagonal con subdivisión suave
        "rock": (
            '<pattern id="pat_rock" patternUnits="userSpaceOnUse" width="18" height="18">'
            '<line x1="0"  y1="0"  x2="18" y2="18"'
            ' stroke="rgba(0,0,0,0.62)" stroke-width="1.1"/>'
            '<line x1="18" y1="0"  x2="0"  y2="18"'
            ' stroke="rgba(0,0,0,0.62)" stroke-width="1.1"/>'
            '<line x1="9"  y1="0"  x2="9"  y2="18"'
            ' stroke="rgba(0,0,0,0.22)" stroke-width="0.5"/>'
            '<line x1="0"  y1="9"  x2="18" y2="9"'
            ' stroke="rgba(0,0,0,0.22)" stroke-width="0.5"/>'
            '</pattern>'
        ),

        # Relleno antrópico: diagonal sencilla ascendente (lleno antrópico)
        "fill": (
            '<pattern id="pat_fill" patternUnits="userSpaceOnUse" width="11" height="11">'
            '<line x1="0"   y1="11" x2="11"  y2="0"'
            ' stroke="rgba(0,0,0,0.65)" stroke-width="1.3"/>'
            '<line x1="-5.5" y1="11" x2="5.5" y2="0"'
            ' stroke="rgba(0,0,0,0.65)" stroke-width="1.3"/>'
            '<line x1="5.5" y1="11" x2="16.5" y2="0"'
            ' stroke="rgba(0,0,0,0.65)" stroke-width="1.3"/>'
            '</pattern>'
        ),

        # Materia orgánica: ondas suaves con puntos fibrosos
        "organic": (
            '<pattern id="pat_organic" patternUnits="userSpaceOnUse" width="40" height="12">'
            '<path d="M0,6 Q10,2.5 20,6 Q30,9.5 40,6"'
            ' fill="none" stroke="rgba(195,165,100,0.85)" stroke-width="1.2"/>'
            '<path d="M0,11 Q10,7.5 20,11 Q30,14.5 40,11"'
            ' fill="none" stroke="rgba(195,165,100,0.52)" stroke-width="0.85"/>'
            '<circle cx="7"  cy="3.5" r="0.9" fill="rgba(175,145,80,0.58)"/>'
            '<circle cx="24" cy="9"   r="0.9" fill="rgba(175,145,80,0.58)"/>'
            '<circle cx="36" cy="3"   r="0.7" fill="rgba(175,145,80,0.44)"/>'
            '</pattern>'
        ),

        "unknown": (
            '<pattern id="pat_unknown" patternUnits="userSpaceOnUse" width="10" height="10">'
            '<line x1="0" y1="10" x2="10" y2="0"'
            ' stroke="rgba(0,0,0,0.32)" stroke-width="0.85"/>'
            '</pattern>'
        ),
    }
    return d.get(sc, d["unknown"])

# ── sistema de raíces ──────────────────────────────────────────────────────────

def _root_system(sc: str, x0: float, x1: float, y_top: float, h: float,
                 layer_idx: int) -> List[str]:
    if sc not in ("clay","organic","silt") or h < 22:
        return []
    n_main = 5 if sc == "organic" else 3
    parts: List[str] = []

    def branch(px: float, py: float, angle: float,
               length: float, thick: float, depth: int, rseed: int) -> None:
        if length < 4 or depth > 4: return
        ex = px + length * math.sin(angle) * 0.75
        ey = min(y_top + h - 3, py + length * math.cos(angle))
        ex = max(x0+4, min(x1-4, ex))
        alpha = min(0.68, 0.36 + thick*0.09)
        parts.append(
            f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
            f'stroke="rgba(18,8,2,{alpha:.2f})" stroke-width="{thick:.1f}" '
            f'stroke-linecap="round"/>'
        )
        sc1=_prng(rseed*3+1); sc2=_prng(rseed*5+2); sc3=_prng(rseed*13+5)
        branch(ex,ey,angle+(sc1-0.5)*0.42,length*0.73,thick*0.73,depth+1,rseed*7+1)
        if sc2>0.45: branch(ex,ey,angle-0.55-_prng(rseed*9+3)*0.38,length*0.58,thick*0.62,depth+1,rseed*11+4)
        if sc3>0.60: branch(ex,ey,angle+0.62+_prng(rseed*17+6)*0.32,length*0.50,thick*0.56,depth+1,rseed*19+7)

    for i in range(n_main):
        s1=_prng(layer_idx*3000+i*89+11); s2=_prng(layer_idx*3000+i*89+12)
        rx=x0+14+s1*(x1-x0-28); rl=min(h*0.62,28+s2*22)
        rt=2.0+s2*1.4; ra=(s1-0.5)*0.22
        branch(rx,y_top+3,ra,rl,rt,0,layer_idx*200+i*23)
    return parts

# ── piedras volumétricas (grava y roca) ───────────────────────────────────────

def _stones(sc: str, x0: float, x1: float, y_top: float, h: float,
            layer_idx: int) -> List[str]:
    params: Dict[str,Tuple] = {
        "gravel":      (45, 11, 28, 0.54),
        "rock":        (20, 16, 42, 0.58),
        "coarse_sand": (14,  3,  8, 0.70),
    }
    if sc not in params or h < 20: return []
    n,min_r,max_r,mf = params[sc]
    parts: List[str] = []; placed: List[Tuple] = []

    for j in range(n*10):
        if len(placed)>=n: break
        s1=_prng(layer_idx*10000+j*37+1); s2=_prng(layer_idx*10000+j*37+2)
        s3=_prng(layer_idx*10000+j*37+3); s4=_prng(layer_idx*10000+j*37+4)
        rx=min_r+s1*(max_r-min_r); ry=rx*(0.50+s2*0.28)
        mx=rx*mf+2; my=ry*mf+2
        if (x1-x0)<=2*mx or h<=2*my: continue
        cx=x0+mx+s3*(x1-x0-2*mx); cy=y_top+my+s4*(h-2*my)
        if any(math.hypot((cx-ox)/(rx+orx+1),(cy-oy)/(ry+ory+1))<0.96
               for ox,oy,orx,ory in placed): continue
        placed.append((cx,cy,rx,ry)); ang=s1*65-32

        # Colores naturales de piedra
        r_d=int(100+s2*42); g_d=int(92+s1*36); b_d=int(74+s4*30)
        r_m=min(255,r_d+36); g_m=min(255,g_d+30); b_m=min(255,b_d+22)
        r_h=min(255,r_m+42); g_h=min(255,g_m+36); b_h=min(255,b_m+26)
        r_o=max(0,r_d-48);   g_o=max(0,g_d-42);   b_o=max(0,b_d-34)
        htop=f"{r_h:02X}{g_h:02X}{b_h:02X}"; hmid=f"{r_m:02X}{g_m:02X}{b_m:02X}"
        hbot=f"{r_d:02X}{g_d:02X}{b_d:02X}"; outl=f"{r_o:02X}{g_o:02X}{b_o:02X}"
        gid=f"sg{layer_idx}_{j}"

        parts.append(
            f'<radialGradient id="{gid}" cx="0.28" cy="0.22" r="0.75"'
            f' gradientUnits="objectBoundingBox">'
            f'<stop offset="0%"   stop-color="#{htop}"/>'
            f'<stop offset="50%"  stop-color="#{hmid}"/>'
            f'<stop offset="100%" stop-color="#{hbot}"/>'
            f'</radialGradient>'
        )
        parts.append(
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"'
            f' fill="url(#{gid})" stroke="#{outl}" stroke-width="1.0"'
            f' transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})"/>'
        )
        hx=cx-rx*0.26; hy=cy-ry*0.30; hrx=rx*0.28; hry=ry*0.20
        parts.append(
            f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{hrx:.1f}" ry="{hry:.1f}"'
            f' fill="rgba(255,255,255,0.52)"'
            f' transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})"/>'
        )
    return parts

# ── pasto superficial ──────────────────────────────────────────────────────────

def _grass_blades(x0: float, x1: float, y_base: float) -> str:
    parts: List[str] = []
    parts.append(
        f'<rect x="{x0}" y="{y_base-7:.1f}" width="{x1-x0}" height="8"'
        f' fill="rgba(8,4,1,0.88)"/>'
    )
    n = max(22, int((x1-x0)/5.0))
    for i in range(n):
        s1=_prng(i*17+1); s2=_prng(i*17+2); s3=_prng(i*17+3); s4=_prng(i*17+4)
        gx=x0+i*(x1-x0)/n+s1*6-3; gh=18+s2*30
        gw=(s3-0.5)*10; gcx=gx+gw*0.4; gcy=y_base-gh*0.55
        gtx=gx+gw; gty=y_base-gh
        r=int(10+s4*26); g=int(55+s2*72); b=int(5+s1*14)
        rt=int(24+s3*36); gt2=int(70+s1*82); bt=int(6+s2*16)
        sw=1.5+s1*1.0
        parts.append(
            f'<path d="M{gx:.1f},{y_base:.1f} Q{gcx:.1f},{gcy:.1f} {gtx:.1f},{gty:.1f}"'
            f' fill="none" stroke="rgb({r},{g},{b})" stroke-width="{sw:.1f}" stroke-linecap="round"/>'
        )
        mx=gx+(gtx-gx)*0.55; my=y_base+(gty-y_base)*0.55
        parts.append(
            f'<path d="M{mx:.1f},{my:.1f} Q{gcx:.1f},{gcy*0.85:.1f} {gtx:.1f},{gty:.1f}"'
            f' fill="none" stroke="rgb({rt},{gt2},{bt})" stroke-width="{sw*0.45:.1f}" stroke-linecap="round"/>'
        )
    return "\n".join(parts)

# ── bordes suavizados (Catmull-Rom) ───────────────────────────────────────────

def _catmull_rom(pts: List[Tuple[float,float]], alpha: float=0.42) -> str:
    if not pts: return ""
    if len(pts)<2: return f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"
    n=len(pts); d=f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"
    for i in range(1,n):
        p0=pts[max(0,i-2)]; p1=pts[i-1]; p2=pts[i]; p3=pts[min(n-1,i+1)]
        cp1x=p1[0]+(p2[0]-p0[0])*alpha/2; cp1y=p1[1]+(p2[1]-p0[1])*alpha/2
        cp2x=p2[0]-(p3[0]-p1[0])*alpha/2; cp2y=p2[1]-(p3[1]-p1[1])*alpha/2
        d+=f" C{cp1x:.2f},{cp1y:.2f} {cp2x:.2f},{cp2y:.2f} {p2[0]:.2f},{p2[1]:.2f}"
    return d

def _layer_path(top: List[Tuple[float,float]], bot: List[Tuple[float,float]]) -> str:
    top_d=_catmull_rom(top)
    rev=list(reversed(bot)); conn=f" L{rev[0][0]:.2f},{rev[0][1]:.2f}"
    n=len(rev); a=0.42; segs: List[str]=[]
    for i in range(1,n):
        p0=rev[max(0,i-2)]; p1=rev[i-1]; p2=rev[i]; p3=rev[min(n-1,i+1)]
        cp1x=p1[0]+(p2[0]-p0[0])*a/2; cp1y=p1[1]+(p2[1]-p0[1])*a/2
        cp2x=p2[0]-(p3[0]-p1[0])*a/2; cp2y=p2[1]-(p3[1]-p1[1])*a/2
        segs.append(f"C{cp1x:.2f},{cp1y:.2f} {cp2x:.2f},{cp2y:.2f} {p2[0]:.2f},{p2[1]:.2f}")
    return top_d+conn+" "+" ".join(segs)+" Z"

_AMPLITUDE: Dict[str,float] = {
    "clay":2.8,"silt":2.0,"fine_sand":1.2,"medium_sand":1.0,
    "coarse_sand":2.8,"gravel":4.0,"rock":5.5,"fill":3.2,
    "organic":5.0,"unknown":2.8,
}

def _boundary_pts(x0: float, x1: float, y: float,
                  amplitude: float, seed: int, n: int=18) -> List[Tuple[float,float]]:
    pts: List[Tuple[float,float]] = [(x0,y)]
    for i in range(1,n):
        t=i/n; x=x0+(x1-x0)*t
        dy=(amplitude*0.58*math.sin(seed*3.7+t*math.pi*2.4)+
            amplitude*0.42*math.sin(seed*1.3+t*math.pi*5.1))
        pts.append((round(x,2),round(y+dy,2)))
    pts.append((x1,y))
    return pts

# ── servicio principal ─────────────────────────────────────────────────────────

class StratigraphicProfile3DService:
    """
    Perfil estratigráfico 3D — patrones USCS limpios estilo AutoCAD.
    Offline. Solo stdlib Python.
    """
    W        = 960
    HEADER_H = 52
    SEC_X    = 75
    SEC_W    = 225
    EXT_DX   = 38
    EXT_DY   = 19
    Y0       = 130
    LEG_X    = 358   # SEC_X + SEC_W + EXT_DX + 20 margin
    FF       = "Arial, Helvetica, sans-serif"

    def _ppm(self, depth: float) -> float:
        return max(500.0, min(1200.0, 110.0*depth)) / depth

    def _interval(self, depth: float) -> float:
        if depth<=3.0:  return 0.25
        if depth<=8.0:  return 0.5
        if depth<=20.0: return 1.0
        return 2.0

    def _target_depth(self, pisos: int) -> float:
        """Profundidad total del perfil según número de pisos."""
        if pisos <= 3:  return 6.0
        if pisos <= 10: return 15.0
        return 25.0

    def _build_layers(self, perf: List[Dict]) -> List[Dict]:
        layers: List[Dict] = []; prev=0.0
        for item in (perf or []):
            try:   end=float(str(item.get("profundidad_z") or 0).replace(",","."))
            except: end=prev+1.0
            if end<=prev: end=prev+0.5
            tipo  = str(item.get("tipo_suelo_principal") or "").strip()
            desc  = str(item.get("descripcion_suelo")    or tipo).strip()
            color = str(item.get("color_predominante")   or "").strip()
            sc    = _classify(tipo, desc)
            hex6  = _fill_color(color, sc)
            layers.append({
                "d0":prev,"d1":end,"esp":round(end-prev,3),
                "sc":sc,"hex":hex6,
                "label":_SOIL_LABELS.get(sc,"Suelo"),
                "desc": desc or _SOIL_LABELS.get(sc,"Suelo"),
            })
            prev=end
        return layers

    def _header(self, project_name: str, sondeo: str, fecha: str) -> str:
        w=self.W; h1=34; h2=self.HEADER_H-h1
        proj=_esc((project_name or "")[:72])
        return "\n".join([
            f'<rect x="0" y="0" width="{w}" height="{h1}" fill="#182E48"/>',
            f'<rect x="0" y="0" width="4" height="{h1}" fill="#3A7FC1"/>',
            f'<text x="{w//2}" y="22" text-anchor="middle" font-family="{self.FF}"'
            f' font-size="13.5" font-weight="bold" letter-spacing="1.5" fill="#FFFFFF"'
            f' filter="url(#gTS)">PERFIL ESTRATIGRÁFICO 3D DEL SUELO</text>',
            f'<rect x="0" y="{h1}" width="{w}" height="{h2}" fill="#26527A"/>',
            f'<text x="12" y="{h1+14}" font-family="{self.FF}" font-size="7.5" fill="#BDD8F0">'
            f'<tspan font-weight="bold" fill="#FFFFFF">PROYECTO: </tspan>{proj}</text>',
            f'<text x="{w//2}" y="{h1+14}" text-anchor="middle" font-family="{self.FF}"'
            f' font-size="7.5" fill="#BDD8F0">'
            f'<tspan font-weight="bold" fill="#FFFFFF">SONDEO: </tspan>{_esc(sondeo)}</text>',
            f'<text x="{w-12}" y="{h1+14}" text-anchor="end" font-family="{self.FF}"'
            f' font-size="7.5" fill="#BDD8F0">'
            f'<tspan font-weight="bold" fill="#FFFFFF">FECHA: </tspan>{_esc(fecha)}</text>',
            f'<line x1="0" y1="{self.HEADER_H}" x2="{w}" y2="{self.HEADER_H}"'
            f' stroke="#3A7FC1" stroke-width="1.5"/>',
        ])

    def _defs(self, layers: List[Dict],
              boundaries: List[List[Tuple[float,float]]],
              ppm: float, defs_extra: List[str]) -> str:
        used={l["sc"] for l in layers}
        P: List[str] = ["<defs>"]

        # Patrones USCS
        for sc in used:
            P.append(f"  {_pattern(sc)}")

        # Clip paths por capa
        for i,_ in enumerate(layers):
            path=_layer_path(boundaries[i],boundaries[i+1])
            P.append(f'  <clipPath id="cpl{i}"><path d="{path}"/></clipPath>')

        # Gradientes de iluminación por capa
        for i,lay in enumerate(layers):
            h6=lay["hex"]; ys=self.Y0+lay["d0"]*ppm; he=lay["esp"]*ppm
            ct=_lighten(h6,0.28); cb=_darken(h6,0.22)
            P.append(
                f'  <linearGradient id="gL{i}" x1="0" y1="{ys:.1f}"'
                f' x2="0" y2="{ys+he:.1f}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0%"   stop-color="#{ct}"/>'
                f'<stop offset="25%"  stop-color="#{h6}"/>'
                f'<stop offset="100%" stop-color="#{cb}"/>'
                f'</linearGradient>'
            )
            # Cara lateral derecha (oscura, pronunciada)
            cr0=_darken(h6,0.48); cr1=_darken(h6,0.65)
            P.append(
                f'  <linearGradient id="gR{i}" x1="0" y1="{ys:.1f}"'
                f' x2="0" y2="{ys+he:.1f}" gradientUnits="userSpaceOnUse">'
                f'<stop offset="0%"   stop-color="#{cr0}"/>'
                f'<stop offset="100%" stop-color="#{cr1}"/>'
                f'</linearGradient>'
            )

        # Cap superior
        if layers:
            ct=_lighten(layers[0]["hex"],0.55); ct2=layers[0]["hex"]
            P.append(
                f'  <linearGradient id="gTop" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0%"   stop-color="#{ct}"/>'
                f'<stop offset="100%" stop-color="#{ct2}"/>'
                f'</linearGradient>'
            )

        # Brillo especular leve (borde izquierdo)
        P.append(
            '  <linearGradient id="gEdge" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0%"   stop-color="#FFF" stop-opacity="0.22"/>'
            '<stop offset="14%"  stop-color="#FFF" stop-opacity="0.0"/>'
            '</linearGradient>'
        )
        # Sombra de drop
        P.append(
            '  <filter id="gShd" x="-8%" y="-4%" width="128%" height="120%">'
            '<feGaussianBlur in="SourceAlpha" stdDeviation="10" result="b"/>'
            '<feOffset dx="9" dy="14" result="o"/>'
            '<feFlood flood-color="rgba(0,0,0,0.38)" result="c"/>'
            '<feComposite in="c" in2="o" operator="in" result="s"/>'
            '<feBlend in="SourceGraphic" in2="s" mode="normal"/>'
            '</filter>'
        )
        # Sombra de texto
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
        x0,x1=self.SEC_X,self.SEC_X+self.SEC_W; dx,dy=self.EXT_DX,self.EXT_DY
        y=top_pts[0][1]
        pts=f"{x0},{y:.1f} {x1},{y:.1f} {x1+dx},{y-dy:.1f} {x0+dx},{y-dy:.1f}"
        return (
            f'<polygon points="{pts}" fill="#C0B490"'
            f' stroke="rgba(0,0,0,0.55)" stroke-width="1.0"/>'
            f'<polygon points="{pts}" fill="url(#gTop)" opacity="0.78"/>'
        )

    def _draw_layer(self, lay: Dict, idx: int,
                    top_pts: List[Tuple[float,float]],
                    bot_pts: List[Tuple[float,float]],
                    ppm: float, is_last: bool,
                    defs_extra: List[str]) -> str:
        sc=lay["sc"]; hex6=lay["hex"]
        ys=self.Y0+lay["d0"]*ppm; he=lay["esp"]*ppm
        x0=self.SEC_X; x1=self.SEC_X+self.SEC_W
        P: List[str]=[]

        # 1. Relleno base (color + gradiente de iluminación)
        P.append(
            f'<rect x="{x0}" y="{ys:.1f}" width="{self.SEC_W}" height="{he:.1f}"'
            f' fill="url(#gL{idx})" clip-path="url(#cpl{idx})"/>'
        )

        # 2. Patrón USCS
        pat_op = 0.86
        if sc == "organic":
            pat_op = 0.90   # fondo oscuro — líneas claras necesitan opacidad alta
        P.append(
            f'<rect x="{x0}" y="{ys:.1f}" width="{self.SEC_W}" height="{he:.1f}"'
            f' fill="url(#pat_{sc})" clip-path="url(#cpl{idx})" opacity="{pat_op:.2f}"/>'
        )

        # 3. Reflejo izquierdo (borde luminoso, efecto 3D)
        if he > 10:
            ew=min(self.SEC_W*0.07, 26)
            P.append(
                f'<rect x="{x0}" y="{ys:.1f}" width="{ew:.1f}" height="{he:.1f}"'
                f' fill="url(#gEdge)" clip-path="url(#cpl{idx})"/>'
            )

        # 6. Borde de capa
        path=_layer_path(top_pts,bot_pts)
        edge=f"#{_darken(hex6,0.52)}"
        P.append(f'<path d="{path}" fill="none" stroke="{edge}" stroke-width="0.9"/>')

        # 7. Cara lateral derecha (extrusión 3D oscura + patrón continuo)
        rty=top_pts[-1][1]; rby=bot_pts[-1][1]
        ext=(f"{x1},{rty:.1f} {x1+self.EXT_DX},{rty-self.EXT_DY:.1f} "
             f"{x1+self.EXT_DX},{rby-self.EXT_DY:.1f} {x1},{rby:.1f}")
        P.append(
            f'<polygon points="{ext}" fill="url(#gR{idx})"'
            f' stroke="{edge}" stroke-width="0.8" stroke-linejoin="round"/>'
        )
        # Patrón en cara lateral para continuidad visual entre caras
        side_op = 0.38 if sc == "organic" else 0.44
        P.append(
            f'<polygon points="{ext}" fill="url(#pat_{sc})"'
            f' stroke="none" opacity="{side_op:.2f}"/>'
        )
        # Arista brillante derecha
        P.append(
            f'<line x1="{x1}" y1="{rty:.1f}" x2="{x1}" y2="{rby:.1f}"'
            f' stroke="rgba(255,255,255,0.45)" stroke-width="1.6"/>'
        )

        return "\n".join(P)

    def _scale(self, layers: List[Dict], ppm: float,
               real_depths: Optional[List[float]] = None) -> str:
        """Escala con marcas en todos los límites reales + profundidad objetivo.
        real_depths: profundidades originales del usuario antes de extender la última capa."""
        total_depth = layers[-1]["d1"]
        sx = self.SEC_X - 10
        bot = self.Y0 + total_depth * ppm
        P: List[str] = [
            f'<line x1="{sx}" y1="{self.Y0:.1f}" x2="{sx}" y2="{bot:.1f}"'
            f' stroke="#2A2A2A" stroke-width="1.5"/>',
        ]

        # Construir set de profundidades a marcar:
        # 1. Todos los límites reales ingresados por el usuario
        # 2. La profundidad objetivo (total_depth) si es mayor
        depths_set: List[float] = [0.0]
        if real_depths:
            for d in real_depths:
                if d not in depths_set:
                    depths_set.append(d)
        else:
            for lay in layers:
                if lay["d1"] not in depths_set:
                    depths_set.append(lay["d1"])
        if total_depth not in depths_set:
            depths_set.append(total_depth)
        depths_set.sort()

        # Profundidad real del usuario (antes de la extensión)
        real_limit = real_depths[-1] if real_depths else total_depth

        x0 = self.SEC_X; x1 = self.SEC_X + self.SEC_W

        for d in depths_set:
            sy = self.Y0 + d * ppm
            is_real   = (real_depths is None) or (d in real_depths) or (d == 0.0)
            is_target = (d == total_depth and d != real_limit)

            # Línea de tick en la escala
            tick_color = "#2A2A2A" if is_real else "#888888"
            P.append(f'<line x1="{sx-8}" y1="{sy:.1f}" x2="{sx}" y2="{sy:.1f}"'
                     f' stroke="{tick_color}" stroke-width="1.5"/>')

            if d > 0:
                label_color = "#1A1A1A" if is_real else "#666666"
                label = f'{d:.2f}m'
                P.append(f'<text x="{sx-11}" y="{sy+4:.1f}" text-anchor="end"'
                         f' font-family="{self.FF}" font-size="10" fill="{label_color}">'
                         f'{label}</text>')

            # Línea horizontal punteada en la columna para el límite real de perforación
            if d == real_limit and is_target is False and real_depths and d != total_depth:
                P.append(
                    f'<line x1="{x0}" y1="{sy:.1f}" x2="{x1}" y2="{sy:.1f}"'
                    f' stroke="rgba(0,0,0,0.35)" stroke-width="1.0"'
                    f' stroke-dasharray="6,4"/>'
                )

        mid = self.Y0 + total_depth * ppm / 2
        P.append(
            f'<text x="{sx-28}" y="{mid:.1f}" text-anchor="middle"'
            f' font-family="{self.FF}" font-size="9.5" fill="#444"'
            f' transform="rotate(-90 {sx-28} {mid:.1f})">Profundidad (m)</text>'
        )
        return "\n".join(P)

    def _legend_table(self, layers: List[Dict]) -> str:
        """Tabla leyenda al costado derecho — ESTRATO | DESCRIPCIÓN MACROSCÓPICA."""
        x    = self.LEG_X
        w    = self.W - x - 18
        sw   = 62          # ancho columna ESTRATO (swatch)
        hdr_h = 28
        row_h = 68
        total_h = hdr_h + len(layers) * row_h + 2
        y0   = self.Y0
        ff   = self.FF
        P: List[str] = []

        # Fondo blanco tabla
        P.append(f'<rect x="{x}" y="{y0}" width="{w}" height="{total_h}"'
                 f' fill="#FFFFFF" stroke="#555555" stroke-width="1.2"/>')

        # Encabezado oscuro
        P.append(f'<rect x="{x}" y="{y0}" width="{w}" height="{hdr_h}" fill="#5A5A5A"/>')

        # Divisor vertical ESTRATO | DESCRIPCION
        vx = x + sw
        P.append(f'<line x1="{vx}" y1="{y0}" x2="{vx}" y2="{y0+total_h}"'
                 f' stroke="#888888" stroke-width="0.9"/>')

        # Textos del encabezado
        P.append(f'<text x="{x + sw//2}" y="{y0 + hdr_h//2 + 5}" text-anchor="middle"'
                 f' font-family="{ff}" font-size="8.5" font-weight="bold" fill="#FFFFFF">'
                 f'ESTRATO</text>')
        P.append(f'<text x="{vx + (w - sw)//2}" y="{y0 + hdr_h//2 + 5}" text-anchor="middle"'
                 f' font-family="{ff}" font-size="8.5" font-weight="bold" fill="#FFFFFF">'
                 f'DESCRIPCIÓN MACROSCÓPICA</text>')

        for i, lay in enumerate(layers):
            yr  = y0 + hdr_h + i * row_h
            sc  = lay["sc"]
            hex6 = lay["hex"]

            # Línea separadora de fila
            P.append(f'<line x1="{x}" y1="{yr}" x2="{x+w}" y2="{yr}"'
                     f' stroke="#BBBBBB" stroke-width="0.7"/>')

            # Swatch (muestra de textura con patrón)
            sx2 = x + 6; sy2 = yr + 6; sw2 = sw - 12; sh2 = row_h - 12
            P.append(f'<rect x="{sx2}" y="{sy2}" width="{sw2}" height="{sh2}"'
                     f' fill="#{hex6}" stroke="#666666" stroke-width="0.8"/>')
            P.append(f'<rect x="{sx2}" y="{sy2}" width="{sw2}" height="{sh2}"'
                     f' fill="url(#pat_{sc})" opacity="0.85"/>')

            # Descripción con word-wrap
            desc = lay["desc"].upper()
            words = desc.split()
            lines_txt: List[str] = []
            cur = ""
            max_chars = max(10, (w - sw - 20) // 6)
            for wrd in words:
                if cur and len(cur) + 1 + len(wrd) > max_chars:
                    lines_txt.append(cur)
                    cur = wrd
                else:
                    cur = (cur + " " + wrd).strip() if cur else wrd
            if cur:
                lines_txt.append(cur)

            line_h = 12
            ty = yr + row_h // 2 - (len(lines_txt) - 1) * line_h // 2
            for ln in lines_txt:
                P.append(f'<text x="{vx + 8}" y="{ty}" font-family="{ff}"'
                         f' font-size="8.5" fill="#111111">{_esc(ln)}</text>')
                ty += line_h

        # Borde inferior
        ybot = y0 + total_h
        P.append(f'<line x1="{x}" y1="{ybot}" x2="{x+w}" y2="{ybot}"'
                 f' stroke="#555555" stroke-width="1.0"/>')
        return "\n".join(P)

    def generate_svg(
        self,
        perforaciones: List[Dict],
        project_name:  str = "",
        sondeo:        str = "P-1",
        fecha               = None,
        pisos:         int  = 0,
    ) -> str:
        from datetime import date as _d
        if fecha is None:             fecha_str=_d.today().strftime("%d/%m/%Y")
        elif hasattr(fecha,"strftime"): fecha_str=fecha.strftime("%d/%m/%Y")
        else:                          fecha_str=str(fecha)

        layers=self._build_layers(perforaciones)
        if not layers:
            return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="200">'
                    f'<rect width="{self.W}" height="200" fill="#F0EDE8"/>'
                    f'<text x="{self.W//2}" y="105" text-anchor="middle"'
                    f' font-family="{self.FF}" font-size="13" fill="#888">Sin datos</text></svg>')

        # Guardar profundidades reales del usuario ANTES de extender
        real_depths: List[float] = [lay["d1"] for lay in layers]

        # Completar profundidad según pisos: la última capa se extiende hasta el target.
        # Las capas del usuario conservan sus profundidades reales; solo se rellena el resto.
        actual_total = layers[-1]["d1"]
        target_d = self._target_depth(pisos) if pisos > 0 else actual_total
        if actual_total > 0 and target_d > actual_total + 0.01:
            layers[-1]["d1"]  = round(target_d, 3)
            layers[-1]["esp"] = round(target_d - layers[-1]["d0"], 3)
        # Si el usuario ingresó más profundidad de la requerida, se respeta su dato

        total_d=layers[-1]["d1"]; ppm=self._ppm(total_d)
        prof_h=total_d*ppm; x0=self.SEC_X; x1=self.SEC_X+self.SEC_W

        boundaries: List[List[Tuple[float,float]]]=[]
        for i,lay in enumerate(layers):
            y_top=self.Y0+lay["d0"]*ppm
            amp=0.0 if i==0 else _AMPLITUDE.get(layers[i-1]["sc"],4.0)*0.80
            boundaries.append(_boundary_pts(x0,x1,y_top,amp,i))
        boundaries.append(_boundary_pts(x0,x1,self.Y0+total_d*ppm,0.0,len(layers)))

        defs_extra: List[str]=[]; layer_svgs: List[str]=[]
        for i,lay in enumerate(layers):
            layer_svgs.append(
                self._draw_layer(lay,i,boundaries[i],boundaries[i+1],
                                 ppm,i==len(layers)-1,defs_extra)
            )

        total_h=int(self.Y0+prof_h+38)
        defs_svg=self._defs(layers,boundaries,ppm,defs_extra)

        border="\n".join([
            f'<line x1="{x0}" y1="{self.Y0:.1f}" x2="{x0}"'
            f' y2="{self.Y0+prof_h:.1f}" stroke="#111" stroke-width="1.8"/>',
            f'<line x1="{x0}" y1="{self.Y0+prof_h:.1f}" x2="{x1}"'
            f' y2="{self.Y0+prof_h:.1f}" stroke="#111" stroke-width="1.2"/>',
        ])
        ext_edges="\n".join([
            f'<line x1="{x1+self.EXT_DX}" y1="{self.Y0-self.EXT_DY:.1f}"'
            f' x2="{x1+self.EXT_DX}" y2="{self.Y0+prof_h-self.EXT_DY:.1f}"'
            f' stroke="#333" stroke-width="1.0"/>',
            f'<line x1="{x1}" y1="{self.Y0+prof_h:.1f}"'
            f' x2="{x1+self.EXT_DX}" y2="{self.Y0+prof_h-self.EXT_DY:.1f}"'
            f' stroke="#333" stroke-width="1.0"/>',
        ])

        ext_overlay_svg = ""

        return "\n".join([
            f'<svg xmlns="http://www.w3.org/2000/svg"'
            f' width="{self.W}" height="{total_h}"'
            f' viewBox="0 0 {self.W} {total_h}">',
            defs_svg,
            f'<rect width="{self.W}" height="{total_h}" fill="#E8E4DC"/>',
            self._header(project_name,sondeo,fecha_str),
            '<g filter="url(#gShd)">',
            self._top_cap(boundaries[0]),
            "\n".join(layer_svgs),
            '</g>',
            border, ext_edges,
            ext_overlay_svg,
            self._scale(layers, ppm, real_depths),
            self._legend_table(layers),
            "</svg>",
        ])

    @staticmethod
    def svg_to_png(svg_path: Path, png_path: Path, width_px: int = 1920) -> Optional[Path]:
        """Convierte SVG → PNG de alta resolución usando Node.js/sharp (sin Cairo).
        Retorna la ruta del PNG generado, o None si falla."""
        import subprocess, shutil, json
        node = shutil.which("node")
        if not node:
            return None
        script = (
            f"const s=require('sharp');"
            f"s(require('fs').readFileSync({json.dumps(str(svg_path))})).resize({{width:{width_px}}})"
            f".png().toFile({json.dumps(str(png_path))},e=>{{if(e){{process.stderr.write(String(e));process.exit(1);}}}});"
        )
        try:
            result = subprocess.run(
                [node, "-e", script],
                capture_output=True, timeout=30,
                cwd=str(svg_path.parent.parent.parent)  # raíz del proyecto (donde está node_modules)
            )
            if result.returncode == 0 and png_path.exists():
                return png_path
        except Exception:
            pass
        return None

    def save_profile_3d(
        self,
        perforaciones: List[Dict],
        output_path:   Path,
        project_name:  str = "",
        sondeo:        str = "P-1",
        fecha               = None,
        pisos:         int  = 0,
    ) -> Path:
        svg = self.generate_svg(perforaciones, project_name, sondeo, fecha, pisos)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(svg, encoding="utf-8")
        # Generar PNG junto al SVG para inserción en Word
        png_path = output_path.with_suffix(".png")
        self.svg_to_png(output_path, png_path)
        return output_path


profile_3d_service = StratigraphicProfile3DService()
