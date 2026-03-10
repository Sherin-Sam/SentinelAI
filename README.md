# AI Voice Scam Interceptor V2 🛡️

A professional-grade, multi-tier security system that protects users by monitoring live calls for scam indicators using real-time audio transcription and a hybrid ML/Heuristic engine.

## 🏗️ System Overview

- **Frontend**: Premium Streamlit Dashboard with real-time threat visualization.
- **Backend**: FastAPI service for analysis and incident logging.
- **Engine**: Real-time microphone listener using `SpeechRecognition` (Google API).
- **Database**: MySQL for persistent incident tracking.

## 🚀 Setup Instructions

### 1. Database Setup
Ensure you have MySQL running and create the database:
```sql
CREATE DATABASE scam_interceptor;
```
*Note: Update `backend/database.py` with your MySQL credentials.*

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*Note: If `PyAudio` fails to install, you may need to install it via [Unofficial Binary](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) or `pip install pipwin; pipwin install pyaudio` on Windows.*

### 3. Run the System (3 Terminals Required)

#### Terminal 1: Backend
```bash
cd backend
uvicorn main:app --reload
```

#### Terminal 2: Frontend
```bash
cd frontend
streamlit run app.py
```

#### Terminal 3: Speech Engine
```bash
python -m engine.listener
```

## 🎤 How the Live Demo Works

1.  **Backend** starts the API server and initializes the MySQL tables.
2.  **Engine** starts listening to your microphone. Talk aloud as if you are a scammer (e.g., "This is the IRS, we need your credit card number or you will be arrested!").
3.  **Frontend** will auto-refresh every 2 seconds to show the latest transcipts and risk scores as they are logged to the database.

## 🚨 V2 Improved Features
- **Separated Concerns**: Clean separation between speech processing and UI.
- **Persistence**: Results are saved and can be audited later.
- **Real-time**: No more simulators; it listens to *your* voice.
- **TF-IDF ML**: More advanced text vectorization for better accuracy.
