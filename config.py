import threading
import locale
import json
import sys
from pathlib import Path

# --- Configuration ---
RECORDING_FILENAME = "temp_recording.wav"
CHUNK = 1024
FORMAT = 8 # pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# filenames
SETTINGS_FILENAME = "settings.json"
LOG_FILENAME = "app.log"

# --- Global State ---
is_recording = False
audio_frames = []
p = None
stream = None
stop_event = threading.Event()
tray_icon = None
icon_red = None
icon_green = None
icon_yellow = None
ctrl_press_timer = None
ctrl_key_pressed = False
listener = None


def get_app_dir() -> Path:
    """Return directory where the script or exe is located."""
    if getattr(sys, 'frozen', False):
        # PyInstaller bundle
        return Path(sys.executable).parent
    return Path(__file__).parent


def get_settings_path() -> Path:
    return get_app_dir() / SETTINGS_FILENAME


def get_log_path() -> Path:
    return get_app_dir() / LOG_FILENAME


def get_default_language():
    """Detects the system's default language and returns a supported language code."""
    language_map = {
        'en': 'en',
        'de': 'de',
        'fr': 'fr',
        'it': 'it'
    }
    try:
        default_lang, _ = locale.getdefaultlocale()
        if default_lang:
            lang_prefix = default_lang.split('_')[0]
            if lang_prefix in language_map:
                return language_map[lang_prefix]
    except Exception:
        # In case locale detection fails
        pass
    return 'en' # Default fallback


# Defaults (may be overridden by load_settings)
current_language = get_default_language()
current_model = "faster_whisper"


def load_settings():
    """Load settings (language, model) from a JSON file next to the script/exe.

    If the file doesn't exist or is invalid, the defaults remain.
    """
    global current_language, current_model
    settings_path = get_settings_path()
    if not settings_path.exists():
        return
    try:
        with settings_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
            lang = data.get('language')
            model = data.get('model')
            if isinstance(lang, str):
                current_language = lang
            if isinstance(model, str):
                current_model = model
    except Exception:
        # If loading fails, ignore and keep defaults
        pass


def save_settings():
    """Persist current settings to the settings file next to the script/exe."""
    settings_path = get_settings_path()
    try:
        with settings_path.open('w', encoding='utf-8') as f:
            json.dump({
                'language': current_language,
                'model': current_model
            }, f, indent=2, ensure_ascii=False)
    except Exception:
        # Best-effort save; ignore failures
        pass


# Load settings at import time so other modules get the persisted values
load_settings()
