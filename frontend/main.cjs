const { app, BrowserWindow, screen } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

// Disable GPU acceleration to prevent crashes on some Windows drivers
app.disableHardwareAcceleration();

let mainWindow;

function createWindow() {
    const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize;

    mainWindow = new BrowserWindow({
        width: 360,
        height: 640,
        x: screenWidth - 400,
        y: screenHeight - 680,
        frame: false,
        transparent: false, // Set to false temporarily for debugging
        alwaysOnTop: true,
        resizable: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        },
        backgroundColor: '#020617', // Match the UI theme
        show: true,
    });

    // Force dev server during hackathon development
    const startURL = 'http://localhost:5174';
    console.log(`Loading URL: ${startURL}`);

    mainWindow.loadURL(startURL).catch(e => {
        console.error(`Failed to load URL: ${e}`);
    });

    mainWindow.on('closed', () => (mainWindow = null));

    // Bridge Logic: Poll backend to auto-show/hide
    setInterval(async () => {
        try {
            const response = await fetch('http://localhost:8000/call-status');
            const state = await response.json();

            if (state.is_active && !mainWindow.isVisible()) {
                console.log("🔔 Call Detected! Showing Window...");
                mainWindow.show();
                mainWindow.focus();
            } else if (!state.is_active && mainWindow.isVisible()) {
                console.log("💤 Call Reset. Hiding Window...");
                mainWindow.hide();
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
