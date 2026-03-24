import os
import eel
import time
from backend.auth import recoganize
from backend.auth.recoganize import AuthenticateFace
from backend.feature import *
from backend.command import *

def start():
    # 1. Initialize the frontend folder
    eel.init("frontend") 
    
    # 2. Expose the init function to JavaScript
    @eel.expose
    def init():
        # Give the browser a split second to register JS functions
        time.sleep(0.5)
        
        # CORRECTED: Removed the extra () from these calls
        eel.hideLoader()
        
        speak("Welcome to Jarvis")
        speak("Ready for Face Authentication")
        
        # Trigger Face Authentication
        flag = recoganize.AuthenticateFace()
        
        if flag == 1:
            speak("Face recognized successfully")
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            speak("Welcome to Your Assistant")
            eel.hideStart()
            eel.showConsole()
            play_assistant_sound()
        else:
            speak("Face not recognized. Please try again")
    
    # 3. Play initial sound and launch the browser
    play_assistant_sound()
    
    # Launch Edge in App Mode
    os.system('start msedge.exe --app="http://127.0.0.1:8000/index.html"')
    
    # 4. Start the Eel server
    eel.start("index.html", mode=None, host="localhost", block=True)