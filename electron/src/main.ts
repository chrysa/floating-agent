/**
 * Floating Agent — Electron main process
 *
 * Responsibilities:
 * - Create and manage the floating overlay window
 * - Spawn and manage the Python daemon subprocess
 * - Handle system tray integration
 * - Set up IPC channels (via preload bridge)
 */

import { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain } from "electron";
import path from "node:path";
import { spawn, ChildProcess } from "node:child_process";

const DAEMON_PORT = 34001;
const DAEMON_URL = `http://127.0.0.1:${DAEMON_PORT}`;
const IS_DEV = process.env.NODE_ENV === "development";
const UI_DEV_URL = "http://localhost:5173";
const UI_PROD_PATH = path.join(__dirname, "../../ui/dist/index.html");

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let daemonProcess: ChildProcess | null = null;

// ─── Daemon management ───────────────────────────────────────────────────────

function startDaemon(): void {
  const daemonDir = IS_DEV
    ? path.join(__dirname, "../../daemon")
    : path.join(process.resourcesPath, "daemon");

  daemonProcess = spawn(
    "python3",
    [
      "-m",
      "uvicorn",
      "floating_agent.main:app",
      "--host",
      "127.0.0.1",
      "--port",
      String(DAEMON_PORT),
      "--no-access-log",
    ],
    { cwd: daemonDir, stdio: ["ignore", "pipe", "pipe"] },
  );

  daemonProcess.stdout?.on("data", (data: Buffer) => {
    console.log(`[daemon] ${data.toString().trim()}`);
  });
  daemonProcess.stderr?.on("data", (data: Buffer) => {
    console.error(`[daemon:err] ${data.toString().trim()}`);
  });
  daemonProcess.on("exit", (code) => {
    console.log(`[daemon] exited with code ${code}`);
  });
}

function stopDaemon(): void {
  if (daemonProcess) {
    daemonProcess.kill();
    daemonProcess = null;
  }
}

// ─── Window management ────────────────────────────────────────────────────────

function createOverlayWindow(): BrowserWindow {
  const win = new BrowserWindow({
    width: 360,
    height: 600,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    movable: true,
    hasShadow: false,
    webPreferences: {
      nodeIntegration: false, // Security: no direct node access in renderer
      contextIsolation: true, // Security: isolated context
      preload: path.join(__dirname, "preload.js"),
    },
  });

  if (IS_DEV) {
    void win.loadURL(UI_DEV_URL);
    win.webContents.openDevTools({ mode: "detach" });
  } else {
    void win.loadFile(UI_PROD_PATH);
  }

  return win;
}

function createTray(win: BrowserWindow): Tray {
  const icon = nativeImage.createEmpty(); // placeholder — replace with actual icon
  const t = new Tray(icon);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: "Show / Hide",
      click: () => (win.isVisible() ? win.hide() : win.show()),
    },
    { type: "separator" },
    { label: "Quit", click: () => app.quit() },
  ]);

  t.setToolTip("Floating Agent");
  t.setContextMenu(contextMenu);
  t.on("click", () => (win.isVisible() ? win.hide() : win.show()));

  return t;
}

// ─── IPC handlers ─────────────────────────────────────────────────────────────

function registerIpcHandlers(): void {
  ipcMain.handle("daemon:url", () => DAEMON_URL);

  ipcMain.on("window:hide", () => mainWindow?.hide());
  ipcMain.on("window:show", () => mainWindow?.show());
}

// ─── App lifecycle ────────────────────────────────────────────────────────────

app.on("ready", () => {
  startDaemon();
  mainWindow = createOverlayWindow();
  tray = createTray(mainWindow);
  registerIpcHandlers();
});

app.on("window-all-closed", () => {
  // Keep alive on macOS; quit on Linux/Windows when all windows are closed
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("before-quit", () => {
  stopDaemon();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    mainWindow = createOverlayWindow();
  }
});
