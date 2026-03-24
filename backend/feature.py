import os
import re
import base64
import sqlite3
import struct
import time
import webbrowser
import subprocess
from io import BytesIO

# --- CRITICAL IMPORTS ---
import eel
import pygame
import requests
import pyaudio
import pyautogui
from PIL import Image
import pywhatkit as kit

# --- LOCAL IMPORTS ---
from backend.command import speak
from backend.config import ASSISTANT_NAME
from backend.helper import extract_yt_term, remove_words

# Initialize database and mixer
conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()
pygame.mixer.init()

# --- EXPOSED UI FUNCTIONS ---

@eel.expose
def play_assistant_sound():
    sound_file = os.path.join("frontend", "assets", "audio", "start_sound.mp3")
    try:
        if os.path.exists(sound_file):
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
        else:
            print(f"Sound file missing: {sound_file}")
    except Exception as e:
        print(f"Sound Error: {e}")

@eel.expose
def process_file(base64_string, file_name):
    """Processes images from the paperclip icon in your HUD console."""
    try:
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        img_data = base64.b64decode(base64_string)
        img = Image.open(BytesIO(img_data))
        
        temp_dir = os.path.join("backend", "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        temp_path = os.path.join(temp_dir, "latest_upload.jpg")
        img.convert('RGB').save(temp_path)
        
        # Diagnostic Update
        eel.execute_js('document.getElementById("matrix-status").innerHTML = "MATRIX: ANALYZING UPLINK";')
        
        speak(f"Sir, visual uplink established for {file_name}. Analyzing now.")
        return analyze_visual_data(base64_string)
    except Exception as e:
        print(f"Visual Error: {e}")
        return "Error"

# --- CORE AI LOGIC ---

def chatBot(query):
    user_input = query.lower()
    # Using 127.0.0.1 is often more stable than 'localhost' on Windows
    url = "http://127.0.0.1:11434/api/generate"
    
    payload = {
        "model": "llama3.2:1b", 
        "prompt": user_input,
        "system": "You are Jarvis, a concise AI assistant. Address the user as Sir.",
        "stream": False
    }
    
    try:
        # Increase timeout to 60 for 4GB VRAM hardware
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            reply = response.json().get("response", "")
            speak(reply.replace("*", ""))
            return reply
        else:
            # This helps identify if the model exists but the server is erroring
            print(f"Ollama Error Code: {response.status_code}")
            speak("Sir, the neural matrix is responding with an error.")
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        speak("Sir, the neural matrix is offline.")

# def chatBot(query):
#     user_input = query.lower()
#     url = "http://localhost:11434/api/generate"
    
#     # ... your payload and persona logic ...

#     # --- THE FIX: Call the exposed JS function ---
#     try:
#         eel.updateStatus("matrix-status", "MATRIX: CALCULATING", "status-active")
#     except:
#         pass

#     try:
#         print("Querying local Ollama matrix...")
#         response = requests.post(url, json=payload, timeout=30)
        
#         if response.status_code == 200:
#             reply = response.json().get("response", "")
#             cleaned_reply = reply.replace("*", "").replace("#", "")
#             speak(cleaned_reply)
            
#             # --- THE FIX: Reset status after completion ---
#             eel.updateStatus("matrix-status", "MATRIX: IDLE")
#             return cleaned_reply
#     except Exception as e:
#         speak("Sir, the neural matrix is offline.")
#         eel.updateStatus("matrix-status", "MATRIX: OFFLINE")
#         return str(e)

# def chatBot(query):
#     user_input = query.lower()
#     url = "http://localhost:11434/api/generate"
    
#     jarvis_persona = (
#         "You are Jarvis, a highly advanced AI assistant. "
#         "Always address the user as 'Sir'. Keep responses concise. "
#         "No emojis. No asterisks."
#     )
    
#     payload = {
#         "model": "llama3.2:1b", 
#         "prompt": user_input,
#         "system": jarvis_persona,
#         "stream": False
#     }
    
#     # Update HUD Matrix Status
#     eel.execute_js('document.getElementById("matrix-status").innerHTML = "MATRIX: CALCULATING";')
#     eel.execute_js('document.getElementById("matrix-status").classList.add("status-active");')

#     try:
#         print("Querying local Ollama matrix...")
#         response = requests.post(url, json=payload, timeout=30)
        
#         if response.status_code == 200:
#             reply = response.json().get("response", "")
#             cleaned_reply = reply.replace("*", "").replace("#", "")
#             speak(cleaned_reply)
            
#             # Reset HUD Matrix Status
#             eel.execute_js('document.getElementById("matrix-status").innerHTML = "MATRIX: IDLE";')
#             eel.execute_js('document.getElementById("matrix-status").classList.remove("status-active");')
#             return cleaned_reply
#     except Exception as e:
#         speak("Sir, the neural matrix is offline.")
#         eel.execute_js('document.getElementById("matrix-status").innerHTML = "MATRIX: OFFLINE";')
#         return str(e)

def analyze_visual_data(base64_image):
    """Utilizes LLaVA for multimodal image analysis."""
    url = "http://127.0.0.1:11434/api/generate" # Use 127.0.0.1 if 'localhost' fails
    payload = {
        "model": "llava", 
        "prompt": "Analyze this image and describe it briefly, Sir.",
        "images": [base64_image],
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            reply = response.json().get("response", "")
            speak(reply.replace("*", ""))
            eel.execute_js('document.getElementById("matrix-status").innerHTML = "MATRIX: IDLE";')
            return reply
    except:
        return "Vision error"

def hotword():
    """Continuous wake-word listener (Free version)."""
    import speech_recognition as sr
    r = sr.Recognizer()
    r.energy_threshold = 300 
    r.dynamic_energy_threshold = True

    while True:
        with sr.Microphone() as source:
            try:
                audio = r.listen(source, timeout=2, phrase_time_limit=2)
                query = r.recognize_google(audio, language='en-in')
                
                if "jarvis" in query.lower():
                    print("Wake word detected: JARVIS")
                    # Ensure HUD shortcut is win+j
                    pyautogui.hotkey('win', 'j')
            except:
                continue

# --- OTHER COMMANDS ---

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "").replace("open", "").strip().lower()
    
    if query:
        # Check Database for local system commands
        cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (query,))
        results = cursor.fetchall()

        if len(results) != 0:
            speak("Opening " + query)
            os.startfile(results[0][0])
        else:
            # Check Web commands
            cursor.execute('SELECT url FROM web_command WHERE name IN (?)', (query,))
            web_results = cursor.fetchall()
            
            if len(web_results) != 0:
                speak("Opening " + query)
                webbrowser.open(web_results[0][0])
            else:
                speak("Opening " + query)
                os.system(f'start {query}')

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak(f"Playing {search_term} on YouTube, Sir.")
    kit.playonyt(search_term)