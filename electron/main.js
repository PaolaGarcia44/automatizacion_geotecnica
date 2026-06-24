'use strict'

const { app, BrowserWindow, dialog, shell, protocol, net, ipcMain, Menu } = require('electron')
const { spawn } = require('child_process')
const path = require('path')
const http = require('http')
const https = require('https')
const fs = require('fs')
const url = require('url')

// ── Constantes ────────────────────────────────────────────────────────────────
const BACKEND_PORT = 8000
const BACKEND_HOST = '127.0.0.1'
const BACKEND_URL = `http://${BACKEND_HOST}:${BACKEND_PORT}`
// Forzar modo producción (app://) siempre que el frontend ya esté compilado en out/
// El servidor Next.js dev causaba problemas con output:'export'. Para desarrollo
// de frontend simplemente ejecuta `npm run build` y reinicia la app.
const IS_DEV = false

let mainWindow = null
let backendProcess = null
let currentTheme = 'light'

// ── Menú de la aplicación ─────────────────────────────────────────────────────
function buildMenu() {
  const template = [
    {
      label: 'Archivo',
      submenu: [
        { role: 'quit', label: 'Salir' },
      ],
    },
    {
      label: 'Editar',
      submenu: [
        { role: 'undo', label: 'Deshacer' },
        { role: 'redo', label: 'Rehacer' },
        { type: 'separator' },
        { role: 'cut', label: 'Cortar' },
        { role: 'copy', label: 'Copiar' },
        { role: 'paste', label: 'Pegar' },
        { role: 'selectAll', label: 'Seleccionar todo' },
      ],
    },
    {
      label: 'Apariencia',
      submenu: [
        {
          label: '☀  Modo claro',
          type: 'radio',
          checked: currentTheme === 'light',
          click: () => {
            currentTheme = 'light'
            mainWindow?.webContents.send('theme:set', 'light')
          },
        },
        {
          label: '🌙  Modo oscuro',
          type: 'radio',
          checked: currentTheme === 'dark',
          click: () => {
            currentTheme = 'dark'
            mainWindow?.webContents.send('theme:set', 'dark')
          },
        },
      ],
    },
    {
      label: 'Ver',
      submenu: [
        { role: 'reload', label: 'Recargar' },
        { role: 'forceReload', label: 'Recargar (forzado)' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Pantalla completa' },
      ],
    },
    {
      label: 'Ventana',
      submenu: [
        { role: 'minimize', label: 'Minimizar' },
        { role: 'close', label: 'Cerrar' },
      ],
    },
  ]
  Menu.setApplicationMenu(Menu.buildFromTemplate(template))
}

// Recibe cambios de tema desde el renderer (sidebar o useTheme)
// y actualiza el checkmark del menú
ipcMain.on('theme:changed', (_event, theme) => {
  currentTheme = theme
  buildMenu()
})

// ── Protocolo personalizado para servir el frontend estático ──────────────────
// Hay que registrar el esquema ANTES de que app esté lista.
protocol.registerSchemesAsPrivileged([
  {
    scheme: 'app',
    privileges: {
      secure: true,
      standard: true,
      supportFetchAPI: true,
      corsEnabled: true,
    },
  },
])

// ── Backend ───────────────────────────────────────────────────────────────────
function startBackend() {
  if (IS_DEV) {
    // Desarrollo: lanzar uvicorn directamente
    const backendDir = path.join(__dirname, '..', 'backend')
    backendProcess = spawn(
      'python',
      ['-m', 'uvicorn', 'main:app',
        '--host', BACKEND_HOST,
        '--port', String(BACKEND_PORT),
        '--reload'],
      { cwd: backendDir, shell: true, stdio: 'pipe' }
    )
  } else {
    // Producción: ejecutable PyInstaller incluido en resources
    const exePath = path.join(
      process.resourcesPath, 'backend', 'autogeo_backend.exe'
    )
    backendProcess = spawn(
      exePath,
      ['--host', BACKEND_HOST, '--port', String(BACKEND_PORT)],
      { stdio: 'pipe' }
    )
  }

  backendProcess.stdout?.on('data', (d) =>
    console.log('[Backend]', d.toString().trimEnd())
  )
  backendProcess.stderr?.on('data', (d) =>
    console.error('[Backend]', d.toString().trimEnd())
  )
  backendProcess.on('error', (err) =>
    console.error('[Backend] Error al iniciar:', err.message)
  )
  backendProcess.on('exit', (code) =>
    console.log('[Backend] Proceso terminó con código:', code)
  )
}

function stopBackend() {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill('SIGTERM')
    backendProcess = null
  }
}

// Espera hasta que el endpoint /health responda 200 (máx. 30 s)
function waitForBackend(timeoutMs = 30_000) {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs
    const check = () => {
      const req = http.get(`${BACKEND_URL}/health`, (res) => {
        if (res.statusCode === 200) return resolve()
        retry()
      })
      req.on('error', retry)
      req.setTimeout(500, () => { req.destroy(); retry() })
    }
    const retry = () => {
      if (Date.now() >= deadline)
        return reject(new Error('El backend no respondió en 30 segundos.'))
      setTimeout(check, 500)
    }
    check()
  })
}

// ── Ventana principal ─────────────────────────────────────────────────────────
// Pantalla de carga mientras el backend arranca
const LOADING_HTML = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>AutoGeo</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      height: 100vh; gap: 24px;
    }
    .logo { font-size: 2rem; font-weight: 700; color: #10b981; letter-spacing: -0.05em; }
    .subtitle { font-size: 0.875rem; color: #64748b; }
    .spinner {
      width: 40px; height: 40px;
      border: 3px solid #1e293b;
      border-top-color: #10b981;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    .msg { font-size: 0.8rem; color: #475569; }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <div class="logo">AutoGeo</div>
  <div class="subtitle">Automatización Geotécnica</div>
  <div class="spinner"></div>
  <div class="msg">Iniciando servidor interno…</div>
</body>
</html>`

let protocolRegistered = false

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'AutoGeo - Automatización Geotécnica',
    show: true,
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: false, // necesario para fetch() desde protocolo app://
    },
  })

  // Mostrar pantalla de carga inmediatamente mientras el backend arranca
  await mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(LOADING_HTML)}`)

  // Esperar a que el backend Python esté listo
  try {
    await waitForBackend()
  } catch (err) {
    dialog.showErrorBox(
      'Error al iniciar AutoGeo',
      `No se pudo iniciar el servidor interno.\n\n${err.message}\n\nRevisa que el puerto ${BACKEND_PORT} esté disponible.`
    )
    app.quit()
    return
  }

  if (IS_DEV) {
    // En desarrollo: carga el servidor Next.js
    await mainWindow.loadURL('http://localhost:3000')
    mainWindow.webContents.openDevTools()
  } else {
    // En producción: registrar protocolo y servir archivos estáticos de out/
    const outDir = path.join(__dirname, '..', 'out')

    if (!protocolRegistered) {
      protocolRegistered = true
      protocol.handle('app', (request) => {
        let reqPath = new URL(request.url).pathname
        // Rutas que terminan en / → index.html del directorio
        if (reqPath.endsWith('/') || reqPath === '') reqPath += 'index.html'
        // Rutas sin extensión → directorio/index.html
        if (!path.extname(reqPath)) reqPath = reqPath.replace(/\/?$/, '/index.html')

        const filePath = path.join(outDir, reqPath)

        if (fs.existsSync(filePath)) {
          return net.fetch(url.pathToFileURL(filePath).toString())
        }
        // Fallback: entregar index.html raíz (SPA navigation)
        return net.fetch(url.pathToFileURL(path.join(outDir, 'index.html')).toString())
      })
    }

    await mainWindow.loadURL('app://-/')
  }

  // Mostrar ventana una vez que el contenido esté listo
  mainWindow.once('ready-to-show', () => mainWindow.show())

  // Abrir links externos en el navegador del sistema, no en Electron
  mainWindow.webContents.setWindowOpenHandler(({ url: openUrl }) => {
    shell.openExternal(openUrl)
    return { action: 'deny' }
  })
}

// ── Descarga directa via IPC (evita problemas de blob URL en renderer) ────────
ipcMain.handle('download-file', async (_event, fileUrl, suggestedName) => {
  // Usar showSaveDialog (asíncrono) para no bloquear el hilo principal
  // mientras el renderer espera la respuesta IPC (showSaveDialogSync causaría deadlock).
  const { filePath: savePath, canceled } = await dialog.showSaveDialog(mainWindow, {
    defaultPath: path.join(app.getPath('documents'), suggestedName || 'documentos.zip'),
    filters: [
      { name: 'Archivos ZIP', extensions: ['zip'] },
      { name: 'Todos los archivos', extensions: ['*'] },
    ],
  })

  if (canceled || !savePath) {
    return { success: false, reason: 'cancelled' }
  }

  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(fileUrl)
    const lib = parsedUrl.protocol === 'https:' ? https : http
    const writeStream = fs.createWriteStream(savePath)

    lib.get(fileUrl, (res) => {
      if (res.statusCode !== 200) {
        writeStream.destroy()
        fs.unlink(savePath, () => {})
        return reject(new Error(`Error del servidor: ${res.statusCode}`))
      }
      res.pipe(writeStream)
      writeStream.on('finish', () => {
        writeStream.close(() => {
          dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Descarga completada',
            message: `Archivo guardado en:\n${savePath}`,
            buttons: ['Abrir carpeta', 'Cerrar'],
          }).then(({ response }) => {
            if (response === 0) shell.openPath(path.dirname(savePath))
          })
          resolve({ success: true, savedPath: savePath })
        })
      })
      writeStream.on('error', (err) => {
        fs.unlink(savePath, () => {})
        reject(err)
      })
    }).on('error', (err) => {
      writeStream.destroy()
      fs.unlink(savePath, () => {})
      reject(err)
    })
  })
})

// ── Ciclo de vida de la app ───────────────────────────────────────────────────
app.whenReady().then(async () => {
  buildMenu()
  startBackend()

  // Crear ventana CON pantalla de carga ANTES de esperar al backend
  // para que el usuario vea que la app arrancó
  await createWindow()
})

app.on('before-quit', stopBackend)
app.on('window-all-closed', () => {
  stopBackend()
  app.quit()
})

app.on('activate', async () => {
  if (BrowserWindow.getAllWindows().length === 0) await createWindow()
})
