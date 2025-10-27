import threading
import locale

# --- Configuration ---
RECORDING_FILENAME = "temp_recording.wav"
CHUNK = 1024
FORMAT = 8 # pyaudio.paInt16
CHANNELS = 1
RATE = 16000

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

current_language = get_default_language()
current_model = "faster_whisper"
