import os
import sys
import re
import random
import datetime
import time
import urllib.parse
import webbrowser
import requests
import xmltodict
import pyjokes
import pyautogui
import pywhatkit
from PIL import Image
from PyQt5 import QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, Qt, QThread
from PyQt5.QtWidgets import QApplication, QMainWindow

from Jarvis import JarvisAssistant
from Jarvis.features.gui import Ui_MainWindow
from Jarvis.config import config

obj = JarvisAssistant()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WALLPAPER_GIF = os.path.join(BASE_DIR, "Jarvis", "utils", "images", "live_wallpaper.gif")
INITIATING_GIF = os.path.join(BASE_DIR, "Jarvis", "utils", "images", "initiating.gif")

# ================================ MEMORY ===========================================================================================================

GREETINGS = [
    "hello deva", "deva", "wake up deva", "you there deva", "time to work deva", "hey deva",
    "ok deva", "are you there deva", "are you there", "hello jarvis", "jarvis", "hey jarvis"
]
GREETINGS_RES = [
    "always there for you boss", "i am ready boss",
    "your wish my command boss", "how can i help you boss?", "i am online and ready boss"
]

EMAIL_DIC = {
    'myself': getattr(config, 'email', ''),
    'my official email': getattr(config, 'email', ''),
    'my second email': getattr(config, 'email', ''),
    'my official mail': getattr(config, 'email', ''),
    'my second mail': getattr(config, 'email', '')
}

CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
# =======================================================================================================================================================


def speak(text):
    if text:
        obj.tts(text)


app_id = getattr(config, 'wolframalpha_id', '')


def computational_intelligence(question):
    try:
        url = "https://api.wolframalpha.com/v2/query"
        params = {"appid": app_id, "input": question, "format": "plaintext"}
        resp = requests.get(url, params=params, timeout=10)
        data = xmltodict.parse(resp.text)
        queryresult = data.get("queryresult", {})
        if queryresult.get("@success") == "true":
            pods = queryresult.get("pod", [])
            if isinstance(pods, dict):
                pods = [pods]
            for pod in pods:
                if pod.get("@title") in ["Result", "Decimal approximation", "Solution", "Exact result", "Definitions"]:
                    subpod = pod.get("subpod", {})
                    if isinstance(subpod, list):
                        subpod = subpod[0]
                    text = subpod.get("plaintext", "")
                    if text:
                        print(text)
                        return text
            if len(pods) > 1:
                subpod = pods[1].get("subpod", {})
                if isinstance(subpod, list):
                    subpod = subpod[0]
                text = subpod.get("plaintext", "")
                if text:
                    print(text)
                    return text
        speak("Sorry boss, I couldn't fetch the answer to your question. Please try again.")
        return None
    except Exception as e:
        print(f"Computational intelligence error: {e}")
        speak("Sorry boss, I couldn't fetch the answer to your question. Please try again.")
        return None


def startup():
    speak("Initializing Deva")
    speak("Starting all systems applications")
    speak("Installing and checking all drivers")
    speak("Calibrating and examining all core processors")
    speak("Checking internet connection")
    speak("All drivers are up and running")
    speak("All systems have been activated")
    speak("Now I am online")
    wish()


def wish():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning Boss")
    elif 12 <= hour < 18:
        speak("Good afternoon Boss")
    else:
        speak("Good evening Boss")
    c_time = obj.tell_time()
    if c_time:
        speak(f"Currently it is {c_time}")
    speak("I am Deva. Online and ready boss. Please tell me how may I help you")


def handle_note_request(command):
    target_app = "vscode" if any(k in command for k in ["vs code", "vscode", "code"]) else "notepad"

    note_text = ""
    patterns = [
        r'(?:open\s+notepad\s+and\s+write|write\s+in\s+notepad|type\s+in\s+notepad|write\s+to\s+notepad)\s+(.*)',
        r'(?:open\s+vs\s*code\s+and\s+write|write\s+in\s+vs\s*code|write\s+to\s+vs\s*code)\s+(.*)',
        r'(?:make\s+a\s+note\s+of|take\s+a\s+note\s+of|take\s+a\s+note|make\s+a\s+note|write\s+this\s+down|remember\s+this|note\s+down)\s*(.*)'
    ]
    for pattern in patterns:
        m = re.search(pattern, command, re.IGNORECASE)
        if m and m.group(1).strip():
            note_text = m.group(1).strip()
            break

    if not note_text:
        speak("What would you like me to write down, boss?")
        note_text = obj.mic_input()

    if note_text:
        success, path = obj.take_note(note_text, app=target_app)
        if success:
            app_label = "VS Code" if target_app == "vscode" else "Notepad"
            speak(f"I have written your note into {app_label}, boss.")
            print(f"Note saved to: {path}")
            return True
        else:
            speak("Sorry boss, couldn't write the note to file.")
            return False
    else:
        speak("I didn't catch that boss, note was not saved.")
        return False


def handle_open_request(command):
    # If user wants to write in an app, redirect to note handler
    if any(k in command for k in ["and write", "write in", "write to", "type in"]):
        return handle_note_request(command)

    match = re.search(r'\b(open|launch|start|run)\b\s*(.*)', command, re.IGNORECASE)
    if not match:
        return False

    verb = match.group(1).lower()
    raw_target = match.group(2).strip()

    if not raw_target:
        speak("What would you like me to open, boss?")
        return False

    is_explicit_web = (
        bool(re.search(r'\b(website|site|webpage|page|url|link|domain)\b', raw_target, re.IGNORECASE))
        or bool(re.search(r'\.(com|in|org|net|edu|gov|io|co|ai|dev|tech)\b', raw_target, re.IGNORECASE))
        or raw_target.startswith('http')
    )
    is_explicit_app = bool(re.search(r'\b(app|application|program|software)\b', raw_target, re.IGNORECASE))

    clean_target = re.sub(r'\b(the|app|application|program|software|website|site|webpage|page|url|link)\b', '', raw_target, flags=re.IGNORECASE).strip()

    if is_explicit_web and not is_explicit_app:
        speak(f"Opening website {clean_target} for you boss")
        return obj.website_opener(raw_target)

    if obj.is_known_app(clean_target) or is_explicit_app:
        speak(f"Opening {clean_target} for you boss")
        res = obj.launch_any_app(clean_target)
        if not res:
            speak(f"Application {clean_target} could not be launched, boss.")
        return res

    if '.' in clean_target:
        speak(f"Opening {clean_target} for you boss")
        return obj.website_opener(clean_target)

    if verb in ['launch', 'run']:
        if obj.launch_any_app(clean_target):
            speak(f"Launching {clean_target} for you boss")
            return True

    speak(f"Opening {clean_target} for you boss")
    return obj.website_opener(clean_target)


def answer_query(question):
    """
    Intelligent answering pipeline:
    1. Persona queries (Creator/Boss Deekshith Reddy, Tumkur)
    2. Google Gemini AI (Deep conversational intelligence & knowledge)
    3. WolframAlpha (Computational & factual math)
    4. Wikipedia (Summaries)
    """
    q_lower = question.lower().strip()

    if any(k in q_lower for k in ["who are you", "what is your name", "what's your name", "what is your identity", "your name"]):
        ans = "I am DEVA, your personal AI voice assistant created by Deekshith Reddy. Always at your service, Boss!"
        print(ans)
        speak(ans)
        return ans

    if any(k in q_lower for k in ["who is your boss", "who is the boss", "who's your boss", "who is boss"]):
        ans = "My boss is Deekshith Reddy."
        print(ans)
        speak(ans)
        return ans

    if any(k in q_lower for k in ["who made you", "who created you", "who is your creator", "who built you", "who designed you"]):
        ans = "I was created and developed by Deekshith Reddy in Tumkur."
        print(ans)
        speak(ans)
        return ans

    if any(k in q_lower for k in ["where are you from", "where do you live", "where are you located", "where were you made"]):
        ans = "I am from Tumkur, Boss."
        print(ans)
        speak(ans)
        return ans

    if any(k in q_lower for k in ["tell me about our boss", "tell me about my boss", "tell me about deekshith", "tell me about deekshith reddy", "about our boss"]):
        ans = "Deekshith Reddy is a brilliant, wonderful developer and visionary from Tumkur. He is my boss and creator."
        print(ans)
        speak(ans)
        return ans

    # 1. Try Gemini AI
    gemini_res = obj.ask_gemini(question)
    if gemini_res:
        print(f"[Gemini AI]: {gemini_res}")
        speak(gemini_res)
        return gemini_res

    # 2. Try WolframAlpha
    wolfram_res = computational_intelligence(question)
    if wolfram_res:
        print(f"[WolframAlpha]: {wolfram_res}")
        speak(wolfram_res)
        return wolfram_res

    # 3. Try Wikipedia
    topic = re.sub(r'^(what\s+is|who\s+is|tell\s+me\s+about|explain)\s+', '', question, flags=re.IGNORECASE).strip()
    if topic:
        wiki_res = obj.tell_me(topic)
        if wiki_res:
            print(f"[Wikipedia]: {wiki_res}")
            speak(wiki_res)
            return wiki_res

    speak("Sorry boss, I couldn't fetch the answer to your question. Please try again.")
    return None


class MainThread(QThread):
    def __init__(self):
        super(MainThread, self).__init__()
        self.last_screenshot = None

    def run(self):
        self.TaskExecution()

    def TaskExecution(self):
        startup()

        while True:
            command = obj.mic_input()
            if not command or not isinstance(command, str):
                time.sleep(0.5)
                continue

            command = command.strip().lower()

            # 1. Persona & Identity
            if any(k in command for k in ["who is your boss", "who is the boss", "who's your boss", "who made you", "who created you", "where are you from", "tell me about our boss", "tell me about deekshith", "who are you", "what is your name", "your name"]):
                answer_query(command)

            # 2. Date & Time
            elif "date" in command and "time" in command:
                date = obj.tell_me_date()
                time_c = obj.tell_time()
                print(f"Date: {date}, Time: {time_c}")
                speak(f"Boss, today's date is {date} and the current time is {time_c}")

            elif re.search(r'\bdate\b', command):
                date = obj.tell_me_date()
                print(date)
                speak(f"Boss, today's date is {date}")

            elif "time" in command:
                time_c = obj.tell_time()
                print(time_c)
                speak(f"Boss, the time is {time_c}")

            # 3. Greetings
            elif command in GREETINGS:
                speak(random.choice(GREETINGS_RES))

            # 4. Note Taking & Writing to Applications (Notepad, VS Code)
            elif any(k in command for k in ["write in notepad", "open notepad and write", "type in notepad", "make a note", "take a note", "write this down", "remember this", "note down", "write in vs code", "open vs code and write"]):
                handle_note_request(command)

            elif "close the note" in command or "close notepad" in command:
                speak("Okay boss, closing notepad")
                os.system("taskkill /f /im notepad.exe")
                os.system("taskkill /f /im notepad++.exe")

            # 5. Open Apps and Websites
            elif re.search(r'\b(open|launch|start|run)\b', command):
                handle_open_request(command)

            # 6. Live Weather
            elif re.search(r'\bweather\b', command):
                parts = command.split('weather', 1)
                city = parts[-1].replace('in', '').replace('of', '').replace('for', '').strip()
                if not city:
                    city = "Hyderabad"
                weather_res = obj.weather(city=city)
                print(weather_res)
                speak(weather_res)

            # 7. News Headlines
            elif "buzzing" in command or "news" in command or "headlines" in command:
                news_res = obj.news()
                if news_res:
                    speak('Source: The Times Of India')
                    speak('Todays Headlines are..')
                    for index, article in enumerate(news_res[:5]):
                        title = article.get('title', '')
                        if title:
                            print(title)
                            speak(title)
                    speak('These were the top headlines, Have a nice day Boss!!')
                else:
                    speak("Sorry boss, I couldn't fetch the latest news at the moment.")

            # 8. Web Searches
            elif 'search google for' in command or 'search for' in command:
                obj.search_anything_google(command)

            elif "play music" in command or "hit some music" in command:
                music_dir = "F://Songs//Imagine_Dragons"
                if os.path.exists(music_dir):
                    songs = os.listdir(music_dir)
                    for song in songs:
                        os.startfile(os.path.join(music_dir, song))
                else:
                    speak("Music directory not found on your system boss.")

            elif 'youtube' in command:
                parts = command.split('youtube', 1)
                video = parts[1].replace('play', '').strip() if len(parts) > 1 else ""
                if not video:
                    video = command.replace('play', '').replace('on youtube', '').strip()
                speak(f"Okay boss, playing {video} on YouTube")
                try:
                    pywhatkit.playonyt(video)
                except Exception as e:
                    print(f"YouTube play error: {e}")
                    urllib_query = urllib.parse.quote(video)
                    webbrowser.open(f"https://www.youtube.com/results?search_query={urllib_query}")

            elif "email" in command or "send email" in command:
                sender_email = getattr(config, 'email', '')
                sender_password = getattr(config, 'email_password', '')

                try:
                    speak("Whom do you want to email boss?")
                    recipient = obj.mic_input()
                    receiver_email = EMAIL_DIC.get(recipient, recipient)
                    if receiver_email and "@" in receiver_email:
                        speak("What is the subject boss?")
                        subject = obj.mic_input()
                        speak("What should I say boss?")
                        message = obj.mic_input()
                        msg = f"Subject: {subject}\n\n{message}"
                        sent = obj.send_mail(sender_email, sender_password, receiver_email, msg)
                        if sent:
                            speak("Email has been successfully sent, boss")
                        else:
                            speak("Failed to send email boss. Please check your credentials.")
                    else:
                        speak("I couldn't find a valid email address boss. Please try again.")
                except Exception as e:
                    print(f"Email error: {e}")
                    speak("Sorry boss. Couldn't send your email. Please try again.")

            elif "what do i have" in command or "do i have plans" in command or "am i busy" in command:
                obj.google_calendar_events(command)

            # 9. Smart AI & Knowledge Questions (Gemini, Wolfram, Wikipedia)
            elif any(k in command for k in ["what is", "who is", "why is", "how to", "how do", "calculate", "tell me about", "explain", "meaning of"]):
                answer_query(command)

            elif "joke" in command:
                try:
                    joke = pyjokes.get_joke()
                    print(joke)
                    speak(joke)
                except Exception as e:
                    print(e)
                    speak("Why do programmers prefer dark mode? Because light attracts bugs!")

            elif "system" in command:
                sys_info = obj.system_info()
                print(sys_info)
                speak(sys_info)

            elif "where is" in command:
                place = command.split('where is ', 1)[1].strip()
                current_loc, target_loc, distance = obj.location(place)
                if target_loc:
                    city = target_loc.get('city', '')
                    state = target_loc.get('state', '')
                    country = target_loc.get('country', '')
                    if city:
                        res = f"{place} is in {state} and country {country}. It is approximately {distance} kilometers away from your current location, boss"
                    else:
                        res = f"{state} is in {country}. It is approximately {distance} kilometers away from your current location, boss"
                    print(res)
                    speak(res)
                else:
                    res = "Sorry boss, I couldn't get the coordinates of the location you requested."
                    speak(res)

            elif "ip address" in command:
                try:
                    ip = requests.get('https://api.ipify.org', timeout=5).text
                    print(ip)
                    speak(f"Boss, your IP address is {ip}")
                except Exception as e:
                    print(e)
                    speak("Unable to fetch IP address at the moment, boss.")

            elif "switch the window" in command or "switch window" in command:
                speak("Okay boss, Switching window")
                pyautogui.keyDown("alt")
                pyautogui.press("tab")
                time.sleep(0.5)
                pyautogui.keyUp("alt")

            elif "where i am" in command or "current location" in command or "where am i" in command:
                try:
                    city, state, country = obj.my_location()
                    print(city, state, country)
                    speak(f"Boss, you are currently in {city}, {state}, {country}")
                except Exception as e:
                    print(e)
                    speak("Sorry boss, I couldn't fetch your current location.")

            elif "take screenshot" in command or "take a screenshot" in command or "capture the screen" in command:
                speak("By what name do you want to save the screenshot boss?")
                name = obj.mic_input()
                if not name:
                    name = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                speak("Alright boss, taking screenshot")
                img = pyautogui.screenshot()
                self.last_screenshot = f"{name}.png"
                img.save(self.last_screenshot)
                speak("The screenshot has been successfully captured, boss")

            elif "show me the screenshot" in command or "open screenshot" in command:
                if self.last_screenshot and os.path.exists(self.last_screenshot):
                    try:
                        img = Image.open(self.last_screenshot)
                        img.show()
                        speak("Here it is boss")
                    except Exception as e:
                        print(e)
                        speak("Sorry boss, I am unable to display the screenshot")
                else:
                    speak("No recent screenshot found boss")

            elif "hide all files" in command or "hide this folder" in command:
                os.system("attrib +h /s /d")
                speak("Boss, files in this folder are now hidden")

            elif "visible" in command or "make files visible" in command:
                os.system("attrib -h /s /d")
                speak("Boss, files in this folder are now visible")

            elif "goodbye" in command or "offline" in command or "bye" in command or "exit" in command:
                speak("Alright boss, going offline. It was nice working with you")
                sys.exit()


startExecution = MainThread()


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.startTask)
        self.ui.pushButton_2.clicked.connect(self.close)
        self.movie_wallpaper = None
        self.movie_initiating = None

    def startTask(self):
        if os.path.exists(WALLPAPER_GIF):
            self.movie_wallpaper = QtGui.QMovie(WALLPAPER_GIF)
            self.ui.label.setMovie(self.movie_wallpaper)
            self.movie_wallpaper.start()

        if os.path.exists(INITIATING_GIF):
            self.movie_initiating = QtGui.QMovie(INITIATING_GIF)
            self.ui.label_2.setMovie(self.movie_initiating)
            self.movie_initiating.start()

        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)

        if not startExecution.isRunning():
            startExecution.start()

    def showTime(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        label_time = current_time.toString('hh:mm:ss')
        label_date = current_date.toString(Qt.ISODate)
        self.ui.textBrowser.setText(label_date)
        self.ui.textBrowser_2.setText(label_time)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    jarvis = Main()
    jarvis.show()
    sys.exit(app.exec_())
