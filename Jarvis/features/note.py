import os
import subprocess
import datetime


def get_notes_directory():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if os.path.exists(desktop):
        notes_dir = os.path.join(desktop, "DEVA_Notes")
    else:
        notes_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Notes")
    os.makedirs(notes_dir, exist_ok=True)
    return notes_dir


def note(text, filename=None, app="notepad"):
    """
    Writes text into a note file and immediately opens it in Notepad or VS Code with text displayed.
    """
    if not text:
        return False, None

    notes_dir = get_notes_directory()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if not filename:
        filename = f"note_{timestamp}.txt"
    elif not filename.endswith((".txt", ".md", ".py", ".html", ".js")):
        filename = f"{filename}.txt"

    note_path = os.path.abspath(os.path.join(notes_dir, filename))
    header = f"--- Note taken by DEVA for Boss on {datetime.datetime.now().strftime('%b %d, %Y at %I:%M %p')} ---\n\n"
    content = header + str(text).strip() + "\n"

    try:
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(content)

        if app in ["code", "vscode", "vs code"]:
            subprocess.Popen(f'code "{note_path}"', shell=True)
        else:
            subprocess.Popen(f'notepad.exe "{note_path}"', shell=True)

        return True, note_path
    except Exception as e:
        print(f"Error saving/opening note: {e}")
        return False, None


