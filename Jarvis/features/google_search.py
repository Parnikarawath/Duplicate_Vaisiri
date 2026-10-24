import webbrowser
import urllib.parse
import re


def speak(text):
    from Jarvis import speak_text
    speak_text(text)


def google_search(command):
    try:
        reg_ex = re.search('search google for (.*)', command)
        if reg_ex:
            search_for = reg_ex.group(1).strip()
        elif 'search for' in command:
            search_for = command.split('search for', 1)[1].strip()
        elif 'for' in command:
            search_for = command.split('for', 1)[1].strip()
        else:
            search_for = command.replace('search', '').replace('google', '').strip()

        speak("Okay boss!")
        speak(f"Searching for {search_for}")

        url = f"https://www.google.com/search?q={urllib.parse.quote(search_for)}"
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Google Search Error: {e}")
        return False