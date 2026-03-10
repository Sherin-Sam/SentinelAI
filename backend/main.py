from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database
import detector
import json
import time

# --- Global Call State (for Auto-Popup) ---
call_state = {
    "is_active": False,
    "last_trigger": 0,
    "caller_name": "Inbound Call"
}

app = FastAPI(title="AI Voice Scam Interceptor API")

# Setup CORS for React/Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB (Simple way for hackathon)
@app.on_event("startup")
def startup():
    try:
        database.init_db()
    except Exception as e:
        print(f"Database initialization failed: {e}. Ensure MySQL is running and 'scam_interceptor' DB exists.")

@app.post("/analyze")
def analyze_call(transcript: str, db: Session = Depends(database.get_db)):
    # Run detection
    scam_engine = detector.ScamDetectorV2()
    result = scam_engine.analyze_text(transcript)
    
    # Save to DB
    log_entry = database.IncidentLog(
        transcript=transcript,
        risk_score=result['score'],
        indicators=json.dumps(result['indicators']),
        action_taken="Alerted" if result['score'] > 70 else "Monitored"
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    return result

@app.get("/logs")
def get_logs(limit: int = 10, db: Session = Depends(database.get_db)):
    logs = db.query(database.IncidentLog).order_by(database.IncidentLog.timestamp.desc()).limit(limit).all()
    return logs

# --- Signal Bridge Endpoints for V3 ---

@app.post("/trigger-call")
def trigger_call(caller: str = "Unknown"):
    call_state["is_active"] = True
    call_state["last_trigger"] = time.time()
    call_state["caller_name"] = caller
    print(f"🔔 CALL TRIGGERED: {caller}")
    return {"status": "triggered", "caller": caller}

@app.get("/call-status")
def get_call_status():
    # Auto-expire trigger after 300 seconds (5 mins) for demo stability
    if call_state["is_active"] and (time.time() - call_state["last_trigger"] > 300):
        call_state["is_active"] = False
    return call_state

@app.post("/reset-call")
def reset_call(db: Session = Depends(database.get_db)):
    call_state["is_active"] = False
    # Clear logs on reset to ensure next call starts fresh
    db.query(database.IncidentLog).delete()
    db.commit()
    print("🧹 Call State Reset: Logs Purged.")
    return {"status": "reset and cleared"}

@app.delete("/logs")
def clear_logs(db: Session = Depends(database.get_db)):
    db.query(database.IncidentLog).delete()
    db.commit()
    return {"status": "logs_cleared"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "time": time.time()}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SentinelAI Backend on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
