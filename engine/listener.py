import speech_recognition as sr
import requests
import threading
import time
import sys

class RealTimeEngine:
    def __init__(self, api_url="http://localhost:8000/analyze", device_index=None):
        self.recognizer = sr.Recognizer()
        self.device_index = device_index
        try:
            self.microphone = sr.Microphone(device_index=device_index)
        except Exception as e:
            print(f"Warning: Could not initialize microphone: {e}")
            self.microphone = None
            
        self.api_url = api_url
        self.is_running = False
        self.transcript_buffer = []

    def _process_text(self, text):
        if not text.strip(): return
        print(f"🎤 Intercepted: {text}")
        self.transcript_buffer.append(text)
        full_transcript = " ".join(self.transcript_buffer)
        
        try:
            print(f"📡 Sending to AI Brain...")
            response = requests.post(self.api_url, params={"transcript": full_transcript}, timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI Analysis: {result['score']}% Risk | {result['threat_level']}")
            else:
                print(f"⚠️ Backend Error: {response.text}")
        except Exception as e:
            print(f"❌ Connection to Brain Lost: {e}")

    def _callback(self, recognizer, audio):
        if not self.is_running: return
        try:
            text = recognizer.recognize_google(audio)
            self._process_text(text)
        except sr.UnknownValueError:
            pass 
        except Exception as e:
            print(f"Transcription Error: {e}")

    def start_mic(self):
        if not self.microphone:
            print("❌ No Microphone available.")
            return False
        try:
            print(f"🎙️ Activating Microphone (Index {self.device_index})...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.is_running = True
            self.stop_listening = self.recognizer.listen_in_background(self.microphone, self._callback)
            print("🔴 ENGINE LIVE & CAPTURING AUDIO")
            return True
        except Exception as e:
            print(f"Hardware Error: {e}")
            return False

    def stop(self):
        self.is_running = False
        if hasattr(self, 'stop_listening'):
            try: self.stop_listening(wait_for_stop=False)
            except: pass
        print("Engine stopped.")

if __name__ == "__main__":
    dev_idx = 1 # Force Index 1 based on list_audio.py
    
    # Simple arg parse for index
    for i, arg in enumerate(sys.argv):
        if arg == "--index" and i+1 < len(sys.argv):
            dev_idx = int(sys.argv[i+1])

    engine = RealTimeEngine(device_index=dev_idx)
    
    print("\n" + "="*40)
    print("🤖 SENTINELAI: STANDBY")
    print("Watching for Call Signal from Backend...")
    print("="*40)

    try:
        active_session = False
        while True:
            try:
                # Poll Backend for Call Status
                res = requests.get("http://localhost:8000/call-status", timeout=2)
                state = res.json()
                
                if state.get("is_active") and not active_session:
                    print(f"\n🔔 SIGNAL DETECTED: {state.get('caller_name')}")
                    engine.transcript_buffer = [] # Clear previous
                    engine.start_mic()
                    active_session = True
                
                elif not state.get("is_active") and active_session:
                    print("\n💤 Signal Lost. Resetting Engine...")
                    engine.stop()
                    active_session = False
                    
                # Visual heartbeat
                if not active_session:
                    print(".", end="", flush=True)
                    if time.time() % 30 < 1: print("\n[Standby Polling...]")
                    
            except Exception as e:
                # Backend might be offline
                print("?", end="", flush=True)
                
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()
        print("\nExiting Interceptor.")
