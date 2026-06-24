'use strict'

const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  platform: process.platform,
  isElectron: true,

  // Descarga de archivos ZIP
  downloadFile: (fileUrl, suggestedName) =>
    ipcRenderer.invoke('download-file', fileUrl, suggestedName),

  // Tema: recibir cambio desde el menú nativo de Electron
  onThemeSet: (callback) =>
    ipcRenderer.on('theme:set', (_event, theme) => callback(theme)),

  // Tema: notificar al proceso principal cuando el renderer cambia el tema
  // (para actualizar el checkmark del menú)
  notifyThemeChanged: (theme) =>
    ipcRenderer.send('theme:changed', theme),
})
