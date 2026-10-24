import sys
import speech_recognition as sr

try:
    import pythoncom
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

from Jarvis.features import date_time
from Jarvis.features import launch_app
from Jarvis.features import website_open
from Jarvis.features import weather
from Jarvis.features import wikipedia
from Jarvis.features import news
from Jarvis.features import send_email
from Jarvis.features import google_search
from Jarvis.features import google_calendar
from Jarvis.features import note
from Jarvis.features import system_stats
from Jarvis.features import loc
from Jarvis.features import gemini


def speak_text(text, voice_index=0, rate=1):
    """
    Speaks text reliably using native Windows SAPI or pyttsx3 fallback.
    Thread-safe and works seamlessly inside PyQt QThreads.
    """
    if not text:
        return False

    clean_text = str(text).strip()
    if not clean_text:
        return False

    if HAS_WIN32COM and sys.platform.startswith('win'):
        try:
            pythoncom.CoInitialize()
            speaker = win32com.client.Dispatch('SAPI.SpVoice')
            speaker.Rate = rate
            speaker.Volume = 100
            voices = speaker.GetVoices()
            if voices.Count > voice_index:
                speaker.Voice = voices.Item(voice_index)
            speaker.Speak(clean_text)
            pythoncom.CoUninitialize()
            return True
        except Exception as e:
            print(f"SAPI TTS error: {e}")

    if HAS_PYTTSX3:
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 175)
            engine.say(clean_text)
            engine.runAndWait()
            return True
        except Exception as e:
            print(f"pyttsx3 TTS error: {e}")

    print(f"[DEVA Voice]: {clean_text}")
    return False


class JarvisAssistant:
    def __init__(self):
        pass

    def mic_input(self):
        """
        Fetch input from mic
        return: user's voice input as text (lowercased) if success, empty string if fail
        """
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening....")
                r.energy_threshold = 3500
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=6, phrase_time_limit=10)
            try:
                print("Recognizing...")
                command = r.recognize_google(audio, language='en-US').lower()
                print(f'You said: {command}')
                return command
            except sr.UnknownValueError:
                print('Could not understand audio')
                return ""
            except sr.RequestError as e:
                print(f'Could not request results from Google Speech Recognition service; {e}')
                return ""
            except Exception as e:
                print(f'Recognition error: {e}')
                return ""
        except Exception as e:
            print(f"Microphone error: {e}")
            return ""

    def tts(self, text):
        """
        Convert any text to speech
        :param text: text(String)
        :return: True/False
        """
        return speak_text(text)

    def tell_me_date(self):
        return date_time.date()

    def tell_time(self):
        return date_time.time()

    def is_known_app(self, app_name):
        return launch_app.is_known_app(app_name)

    def launch_any_app(self, app_name):
        """
        Launch any Windows application safely
        :param app_name: name or path of app
        :return: True if success, False if fail
        """
        return launch_app.launch_app(app_name)

    def website_opener(self, domain):
        """
        This will open website according to domain
        :param domain: any domain, example "youtube.com"
        :return: True if success, False if fail
        """
        return website_open.website_opener(domain)

    def weather(self, city):
        """
        Return weather
        :param city: Any city of this world
        :return: weather info as string if True, or False
        """
        try:
            res = weather.fetch_weather(city)
        except Exception as e:
            print(e)
            res = False
        return res

    def tell_me(self, topic):
        """
        Tells about anything from wikipedia
        :param topic: any string is valid options
        :return: summary from wikipedia if True, False if fail
        """
        return wikipedia.tell_me_about(topic)

    def news(self):
        """
        Fetch top news of the day from newsapi
        :return: news list of string if True, False if fail
        """
        return news.get_news()

    def send_mail(self, sender_email, sender_password, receiver_email, msg):
        return send_email.mail(sender_email, sender_password, receiver_email, msg)

    def google_calendar_events(self, text):
        service = google_calendar.authenticate_google()
        date = google_calendar.get_date(text)
        if date and service:
            return google_calendar.get_events(date, service)
        elif not service:
            self.tts("Google calendar credentials are not configured.")

    def search_anything_google(self, command):
        google_search.google_search(command)

    def take_note(self, text, filename=None, app="notepad"):
        return note.note(text, filename=filename, app=app)

    def ask_gemini(self, prompt):
        return gemini.ask_gemini(prompt)

    def system_info(self):
        return system_stats.system_stats()

    def location(self, location):
        return loc.loc(location)

    def my_location(self):
        return loc.my_location()