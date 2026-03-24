import pyttsx3
import eel
import threading
import pythoncom
import speech_recognition as sr

# ==============================
# 🔒 GLOBAL LOCK (NO OVERLAP)
# ==============================
speech_lock = threading.Lock()


# ==============================
# 🔊 SPEAK FUNCTION
# ==============================
def speak(text):
    text = str(text)

    # UI update (safe)
    try:
        eel.DisplayMessage(text)
        eel.receiverText(text)
    except:
        pass

    def tts_logic():
        with speech_lock:
            pythoncom.CoInitialize()
            try:
                engine = pyttsx3.init('sapi5')
                voices = engine.getProperty('voices')

                engine.setProperty(
                    'voice',
                    voices[min(2, len(voices) - 1)].id
                )
                engine.setProperty('rate', 174)

                print(f"JARVIS: {text}")

                engine.say(text)
                engine.runAndWait()

                engine.stop()
                del engine

            except Exception as e:
                print(f"Speech Error: {e}")

            finally:
                pythoncom.CoUninitialize()

    threading.Thread(target=tts_logic, daemon=True).start()


# ==============================
# 🎤 VOICE INPUT
# ==============================
def takecommand():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")

        try:
            eel.DisplayMessage("Listening...")
        except:
            pass

        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)

        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=8)
        except Exception as e:
            print("Mic Timeout:", e)
            return None

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-US')

        print(f"User said: {query}")

        try:
            eel.DisplayMessage(query)
        except:
            pass

        return query.lower()

    except Exception as e:
        print("Recognition Error:", e)
        return None


# ==============================
# 🧠 MAIN COMMAND HANDLER
# ==============================
@eel.expose
def takeAllCommands(message=None):

    def run_command():
        query = None

        # ======================
        # GET INPUT
        # ======================
        if message:
            query = message
        else:
            query = takecommand()

        # ======================
        # PROCESS QUERY
        # ======================
        if query:
            try:
                eel.senderText(query)
            except:
                pass

            query_lower = query.lower()

            try:
                if "open" in query_lower:
                    from backend.feature import openCommand
                    openCommand(query)

                elif "play" in query_lower and "youtube" in query_lower:
                    from backend.feature import PlayYoutube
                    PlayYoutube(query)

                elif "send message" in query_lower or "call" in query_lower or "video call" in query_lower:
                    from backend.feature import findContact, whatsApp

                    Phone, name = findContact(query)

                    if Phone != 0:
                        flag = ""

                        if "send message" in query_lower:
                            flag = "message"
                            speak("What message should I send?")
                            msg = takecommand()

                            if msg:
                                whatsApp(Phone, msg, flag, name)
                            else:
                                speak("Message not received")

                        elif "call" in query_lower:
                            flag = "call"
                            whatsApp(Phone, query, flag, name)

                        else:
                            flag = "video call"
                            whatsApp(Phone, query, flag, name)

                else:
                    from backend.feature import chatBot
                    chatBot(query)

            except Exception as e:
                print(f"Command Error: {e}")
                speak("Something went wrong")

        # ======================
        # RETURN UI
        # ======================
        try:
            eel.ShowHood()
        except:
            pass

    threading.Thread(target=run_command, daemon=True).start()