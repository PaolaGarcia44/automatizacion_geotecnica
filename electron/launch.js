'use strict'
// Este launcher elimina ELECTRON_RUN_AS_NODE del entorno antes de iniciar Electron.
// Necesario cuando se desarrolla desde dentro de otra app Electron (ej: Claude Code / VS Code)
// que propaga esa variable y hace que Electron corra en modo Node.js puro.
const { spawn } = require('child_process')
const path = require('path')

const electronPath = require('electron')  // node_modules/electron/index.js → ruta al binario
const appDir = path.join(__dirname, '..')

const env = Object.assign({}, process.env)
delete env.ELECTRON_RUN_AS_NODE

const child = spawn(electronPath, [appDir], {
  env,
  stdio: 'inherit',
  windowsHide: false,
})
child.on('close', (code) => process.exit(code ?? 0))
