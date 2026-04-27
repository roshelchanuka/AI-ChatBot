import pyttsx3
import speech_recognition as sr
import threading

class VoiceEngine:
    def __init__(self):
        # Initialize TTS
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150) # Speed
            self.tts_engine.setProperty('volume', 0.9) # Volume
        except Exception as e:
            print(f"TTS Init Error: {e}")
            self.tts_engine = None

        # Initialize STT
        self.recognizer = sr.Recognizer()

    def speak(self, text, rate=150):
        """Speaks the text in a separate thread."""
        if not self.tts_engine:
            return
            
        def _speak():
            self.tts_engine.setProperty('rate', rate)
            clean_text = text.replace("**", "").replace("#", "").replace("🏝️", "").replace("🏨", "")
            self.tts_engine.say(clean_text)
            self.tts_engine.runAndWait()

        threading.Thread(target=_speak).start()

    def handle_voice_commands(self, text):
        """Checks for special voice shortcuts."""
        text = text.lower()
        if "clear chat" in text or "reset chat" in text:
            return "CMD_CLEAR"
        if "speak faster" in text:
            self.tts_engine.setProperty('rate', 200)
            return "CMD_FAST"
        if "speak slower" in text:
            self.tts_engine.setProperty('rate', 100)
            return "CMD_SLOW"
        return None

    def listen(self):
        """Listens to microphone and returns transcribed text."""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Error: Could not understand audio"
            except sr.RequestError:
                return "Error: Speech service unavailable"
            except Exception as e:
                return f"Error: {str(e)}"

# Singleton
voice = VoiceEngine()

def speak_text(text):
    voice.speak(text)

def listen_voice():
    return voice.listen()
