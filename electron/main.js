// electron/main.js
const { app, BrowserWindow, Tray, Menu } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

let backendProc = null;
let mainWindow = null;
let tray = null;

const isProd = process.env.NODE_ENV === "production";

// --- Backend startup ---
function startBackend() {
  // Expect the frozen backend to live under a `backend` directory next to this file.
  const backendExe = path.join(__dirname, "backend", process.platform === "win32" ? "bdeb_admin_backend.exe" : "bdeb_admin_backend");

  if (!fs.existsSync(backendExe)) {
    console.error("Backend executable not found at", backendExe);
    return;
  }

  backendProc = spawn(backendExe, [], {
    stdio: ["ignore", "pipe", "pipe"],
  });

  backendProc.stdout.on("data", (d) => {
    console.log("[backend]", d.toString().trim());
  });
  backendProc.stderr.on("data", (d) => {
    console.error("[backend error]", d.toString().trim());
  });

  backendProc.on("exit", (code, signal) => {
    console.log(`Backend exited with code=${code} signal=${signal}`);
    // Optionally: notify renderer via IPC that backend died
  });
}

// Poll /admin/ping until backend responds or timeout
async function waitForBackend(timeoutMs = 10000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch("http://127.0.0.1:5001/admin/ping");
      if (res.ok) return true;
    } catch {
      // ignore
    }
    await new Promise((r) => setTimeout(r, 250));
  }
  return false;
}

// --- Windows/app UI setup ---
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1920,
    height: 1080,
    show: false,
    icon: path.join(__dirname, "icon.ico"),
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      // If you have a preload for IPC, specify it here:
      // preload: path.join(__dirname, "preload.js"),
    },
  });

  Menu.setApplicationMenu(null);
  mainWindow.setMenuBarVisibility(false);

  if (!isProd) {
    mainWindow.loadURL("http://localhost:5173/");
  } else {
    mainWindow.loadFile(path.join(__dirname, "../admin-frontend/dist/index.html"));
  }

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function createSplashWindow() {
  const splash = new BrowserWindow({
    width: 954,
    height: 318,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
  });
  splash.loadFile(path.join(__dirname, "splash.html"));
  return splash;
}

function createTray() {
  tray = new Tray(path.join(__dirname, "icon.ico"));
  const ctx = Menu.buildFromTemplate([
    { label: "Show", click: () => mainWindow && mainWindow.show() },
    { label: "Quit", click: () => app.quit() },
  ]);
  tray.setToolTip("BdeB-Go Manager");
  tray.setContextMenu(ctx);
}

app.whenReady().then(async () => {
  const splash = createSplashWindow();

  if (isProd) {
    startBackend();
    const healthy = await waitForBackend(10000);
    if (!healthy) {
      console.warn("Backend did not respond in time; continuing anyway.");
    }
  }

  createMainWindow();
  createTray();

  // close splash once main window is about to show
  splash.close();
});

// --- Clean shutdown ---
app.on("before-quit", () => {
  if (backendProc) {
    backendProc.kill();
  }
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
  if (backendProc) backendProc.kill();
});

// macOS re-open behavior
app.on("activate", () => {
  if (!mainWindow) {
    createMainWindow();
  }
});
