# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec para AutoGeo Backend (compatible con PyInstaller 6.x).

Genera una distribución one-folder. Las plantillas Excel se empaquetan.
Las plantillas Word deben copiarse después a:
    dist/autogeo_backend/templates/word/

Uso:
    cd backend
    ..\.venv\Scripts\pyinstaller.exe autogeo.spec
"""

try:
    from PyInstaller.utils.hooks import collect_submodules, collect_data_files
    _pywin32_hidden = collect_submodules('win32com') + ['win32timezone', 'pywintypes']
    _pywin32_datas = collect_data_files('win32com')
except Exception:
    _pywin32_hidden = []
    _pywin32_datas = []

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Las plantillas Excel se copian manualmente al dist root por build.ps1
        # (PyInstaller 6 pone datas en _internal/, pero config.py busca en exe.parent)
        ('app', 'app'),
    ] + _pywin32_datas,
    hiddenimports=[
        # Uvicorn
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        # FastAPI / Starlette
        'fastapi',
        'starlette',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        # Pydantic
        'pydantic',
        'pydantic.v1',
        'pydantic_settings',
        # Office / documentos
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.utils',
        'docx',
        # pywin32
        'win32api',
        'win32com',
        'win32com.client',
        'win32com.client.gencache',
        'pythoncom',
        # Email / multipart (fastapi file uploads)
        'email.mime',
        'email.mime.multipart',
        'multipart',
    ] + _pywin32_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL', 'cv2', 'numpy', 'scipy'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='autogeo_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='autogeo_backend',
)
