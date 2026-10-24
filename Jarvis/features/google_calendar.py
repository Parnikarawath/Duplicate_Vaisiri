import datetime
import pytz
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENSIONS = ["rd", "th", "st", "nd"]


def speak(text):
    from Jarvis import speak_text
    speak_text(text)


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def authenticate_google():
    """Shows basic usage of the Google Calendar API."""
    try:
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            else:
                return None

        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Google Calendar Auth error: {e}")
        return None


def get_events(day, service):
    if not service:
        speak("Google Calendar is not configured or authenticated.")
        return

    try:
        date = datetime.datetime.combine(day, datetime.datetime.min.time())
        end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
        utc = pytz.UTC
        date = date.astimezone(utc)
        end_date = end_date.astimezone(utc)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=date.isoformat(),
            timeMax=end_date.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            speak('No upcoming events found.')
        else:
            speak(f"You have {len(events)} events on this day.")

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'Event')
                print(start, summary)
                if "T" in str(start):
                    start_time = str(start.split("T")[1].split("+")[0])
                    hour = int(start_time.split(":")[0])
                    if hour < 12:
                        start_time = f"{hour if hour > 0 else 12} am"
                    else:
                        start_time = f"{hour - 12 if hour > 12 else 12} pm"
                else:
                    start_time = "all day"

                speak(f"{summary} at {start_time}")
    except Exception as e:
        print(f"Calendar events error: {e}")
        speak("Unable to retrieve calendar events at this time.")


def get_date(text):
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except Exception:
                        pass

    if month < today.month and month != -1:
        year = year + 1

    if month == -1 and day != -1:
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1 and month != -1:
        return datetime.date(month=month, day=day, year=year)

    return today