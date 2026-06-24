"""
Punto de entrada para el backend empaquetado con PyInstaller.

Uvicorn no puede usar --reload en modo empaquetado, así que
lanzamos el servidor directamente desde aquí con argparse
para que Electron pueda pasar --host y --port.
"""

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description='AutoGeo Backend Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host de escucha')
    parser.add_argument('--port', type=int, default=8000, help='Puerto de escucha')
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        'main:app',
        host=args.host,
        port=args.port,
        reload=False,
        log_level='info',
    )


if __name__ == '__main__':
    main()
