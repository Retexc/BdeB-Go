// electron/main.js
const { app, BrowserWindow, Tray, Menu } = require('electron');
const path = require('path');

let mainWindow, tray;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1920,
    height: 1080,
    show: false,             // don’t show until ready
    icon: path.join(__dirname, 'icon.ico'),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  if (process.env.NODE_ENV !== 'production') {
    mainWindow.loadURL('http://localhost:5173/');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../admin-frontend/dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
}

function createSplashWindow() {
  const splash = new BrowserWindow({
    width: 954,             // match your splash image size
    height: 318,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
  });
  splash.loadFile(path.join(__dirname, 'splash.html'));
  return splash;
}

function createTray() {
  tray = new Tray(path.join(__dirname, 'icon.ico'));
  const ctx = Menu.buildFromTemplate([
    { label: 'Show',   click: () => mainWindow.show() },
    { label: 'Quit',   click: () => app.quit()   }
  ]);
  tray.setToolTip('BdeB‑Go Manager');
  tray.setContextMenu(ctx);
}

app.whenReady().then(() => {
  const splash = createSplashWindow();

  // after 5 seconds, destroy splash, then show main
  setTimeout(() => {
    splash.close();
    createMainWindow();
    createTray();
  }, 5000);
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
