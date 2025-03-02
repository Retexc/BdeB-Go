// electron-main.js (ESM version)
import { app, BrowserWindow } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';

// __filename and __dirname replacements in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const isDev = process.env.NODE_ENV === 'development';

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1920,
    height: 1080,
    title: 'BdeB-Transit',
    icon: path.join(__dirname,'src', 'assets', 'icon.ico'),
    webPreferences: {
      nodeIntegration: true,
    },
  });

  if (isDev) {
    // If in development, load your Vite dev server
    mainWindow.loadURL('http://localhost:5173');
  } else {
    // In production, load the built index.html
    mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
  }
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
