import { app, BrowserWindow, screen } from 'electron';
import path from 'path';
import { fileURLToPath } from 'url';
import isDev from 'electron-is-dev';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow;

function createWindow() {
    const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;

    mainWindow = new BrowserWindow({
        width: 360,
        height: 640,
        x: screenWidth - 400, // Bottom right corner
        y: screenHeight - 680,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        resizable: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
        show: false, // Start hidden
    });

    const startURL = isDev
        ? 'http://localhost:5173'
        : `file://${path.join(__dirname, 'dist/index.html')}`;

    mainWindow.loadURL(startURL);

    mainWindow.on('closed', () => (mainWindow = null));

    // Logic to show window when backend triggers
    setInterval(async () => {
        try {
            const response = await fetch('http://localhost:8000/call-status');
            const state = await response.json();

            if (state.is_active && !mainWindow.isVisible()) {
                mainWindow.show();
                mainWindow.focus();
            }
        } catch (e) {
            // Backend might be down
        }
    }, 1000);
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});
