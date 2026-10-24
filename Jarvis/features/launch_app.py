import os
import subprocess
import re

APP_MAP = {
    'notepad': 'notepad',
    'notepad++': 'notepad++',
    'calculator': 'calc',
    'calc': 'calc',
    'chrome': 'chrome',
    'google chrome': 'chrome',
    'browser': 'chrome',
    'web browser': 'chrome',
    'edge': 'msedge',
    'microsoft edge': 'msedge',
    'vs code': 'code',
    'vscode': 'code',
    'visual studio code': 'code',
    'visual studio': 'devenv',
    'code': 'code',
    'word': 'winword',
    'ms word': 'winword',
    'microsoft word': 'winword',
    'excel': 'excel',
    'ms excel': 'excel',
    'microsoft excel': 'excel',
    'powerpoint': 'powerpnt',
    'ppt': 'powerpnt',
    'ms powerpoint': 'powerpnt',
    'microsoft powerpoint': 'powerpnt',
    'command prompt': 'cmd',
    'cmd': 'cmd',
    'terminal': 'wt',
    'windows terminal': 'wt',
    'powershell': 'powershell',
    'explorer': 'explorer',
    'file explorer': 'explorer',
    'my computer': 'explorer',
    'this pc': 'explorer',
    'files': 'explorer',
    'task manager': 'taskmgr',
    'taskmgr': 'taskmgr',
    'settings': 'ms-settings:',
    'control panel': 'control',
    'camera': 'microsoft.windows.camera:',
    'paint': 'mspaint',
    'mspaint': 'mspaint',
    'spotify': 'spotify',
    'discord': 'discord',
    'vlc': 'vlc',
    'whatsapp': 'whatsapp:',
    'telegram': 'telegram'
}


def is_known_app(name):
    if not name:
        return False
    clean = name.strip().lower()
    clean = re.sub(r'\b(the|app|application|program|software)\b', '', clean).strip()
    return clean in APP_MAP


def launch_app(app_name):
    """
    Launch any Windows application safely and asynchronously.
    """
    if not app_name:
        return False

    clean_name = app_name.strip().lower()
    clean_name = re.sub(r'\b(the|app|application|program|software)\b', '', clean_name).strip()

    target = APP_MAP.get(clean_name, clean_name)

    try:
        if target.startswith("ms-settings:") or target.startswith("microsoft.") or target.endswith(":"):
            os.startfile(target)
            return True

        subprocess.Popen(f'start "" "{target}"', shell=True)
        return True
    except Exception as e:
        print(f"Error launching app '{app_name}': {e}")
        try:
            os.system(f'start {target}')
            return True
        except Exception as e2:
            print(f"Fallback launch failed: {e2}")
            return False