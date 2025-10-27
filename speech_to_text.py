
# Voice-to-Text Transcription Tool
#
# This program listens for a global hotkey, records audio while the key is held down,
# transcribes the audio to text, and types it at the current cursor position.
# It runs as a system tray application.
#
# Required libraries:
# pip install pynput speechrecognition pyaudio pystray pillow
#
# Note: PyAudio may have system-level dependencies.
# On Debian/Ubuntu: sudo apt-get install portaudio19-dev
# On Windows, you can often find pre-compiled wheels if pip fails.

import threading
import ctypes
import locale
import wave
import webbrowser
import pyaudio
import winsound
import speech_recognition as sr
from pynput import keyboard
from pynput.keyboard import Controller as KeyboardController
from pystray import MenuItem, Icon, Menu
from PIL import Image, ImageDraw

# --- Configuration ---
RECORDING_FILENAME = "temp_recording.wav"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

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
current_language = get_default_language()
current_model = "faster_whisper"

def set_model(model_name):
    def on_set_model(icon, item):
        global current_model
        current_model = model_name
    return on_set_model

def is_model_selected(model_name):
    def on_is_selected(item):
        global current_model
        return current_model == model_name
    return on_is_selected

def create_image(color):
    """Creates an icon image with a colored dot."""
    width, height = 64, 64
    background = "black"
    image = Image.new("RGB", (width, height), background)
    dc = ImageDraw.Draw(image)
    dc.ellipse([(10, 10), (width - 10, height - 10)], fill=color)
    return image

def set_clipboard(text):
    """Copies the given text to the clipboard using the Windows API."""
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')

    # Define argtypes and restypes for clarity and correctness
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.restype = ctypes.c_bool
    user32.OpenClipboard.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.restype = ctypes.c_bool
    user32.EmptyClipboard.restype = ctypes.c_bool
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p
    user32.CloseClipboard.restype = ctypes.c_bool

    GMEM_DDESHARE = 0x2000
    CF_UNICODETEXT = 13
    
    h_mem = kernel32.GlobalAlloc(GMEM_DDESHARE, len(text.encode('utf-16-le')) + 2)
    if not h_mem:
        return # Failed to allocate memory

    pch_data = kernel32.GlobalLock(h_mem)
    if not pch_data:
        kernel32.GlobalFree(h_mem)
        return # Failed to lock memory

    ctypes.memmove(pch_data, text.encode('utf-16-le'), len(text.encode('utf-16-le')))
    
    kernel32.GlobalUnlock(h_mem)
    
    if user32.OpenClipboard(None):
        user32.EmptyClipboard()
        user32.SetClipboardData(CF_UNICODETEXT, h_mem)
        user32.CloseClipboard()

# --- Core Functions ---

def start_recording():
    """Initializes and starts the audio recording stream."""
    global is_recording, audio_frames, p, stream, tray_icon, icon_green
    if is_recording:
        return

    if tray_icon:
        tray_icon.notify("Recording started...")
        tray_icon.icon = icon_green
    
    winsound.Beep(1000, 200)

    print("Starting recording...")
    is_recording = True
    audio_frames = []
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    # Recording loop runs in a separate thread
    threading.Thread(target=record_loop).start()

def record_loop():
    """Continuously records audio chunks until recording is stopped."""
    global stream, audio_frames
    while is_recording:
        try:
            data = stream.read(CHUNK)
            audio_frames.append(data)
        except IOError:
            # This can happen if the stream is closed while reading
            break

def stop_recording_and_transcribe():
    """Stops recording, saves the audio, and initiates transcription."""
    global is_recording, p, stream, tray_icon, icon_yellow
    if not is_recording:
        return

    if tray_icon:
        tray_icon.icon = icon_yellow
        tray_icon.notify("Transcribing...")

    print("Stopping recording...")
    is_recording = False
    
    # Allow the recording loop to finish
    threading.Timer(0.1, _finish_processing).start()

def _finish_processing():
    """Saves audio to a file and transcribes it."""
    global stream, p, audio_frames, tray_icon, icon_red
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded data as a WAV file
    with wave.open(RECORDING_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_frames))

    print("Audio saved. Transcribing...")
    transcribe_audio(RECORDING_FILENAME)

    if tray_icon:
        tray_icon.icon = icon_red

def transcribe_audio(filename):
    """Converts audio file to text and types it."""
    global current_language, current_model
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        r.adjust_for_ambient_noise(source)
        audio_data = r.record(source)
        try:
            if current_model == "faster_whisper":
                # Using Faster Whisper on CPU
                text = r.recognize_faster_whisper(audio_data, model="tiny", language=current_language, init_options={"device": "cpu"})
                print(f"Recognized with Faster Whisper: {text}")
            else: # google
                google_language_map = {
                    'en': 'en-US',
                    'de': 'de-DE',
                    'fr': 'fr-FR',
                    'it': 'it-IT'
                }
                google_language = google_language_map.get(current_language, 'en-US')
                # Using Google's free web speech API
                text = r.recognize_google(audio_data, language=google_language)
                print(f"Recognized with Google: {text}")
            
            set_clipboard(text)

            # Simulate paste
            keyboard_controller = KeyboardController()
            with keyboard_controller.pressed(keyboard.Key.ctrl):
                keyboard_controller.press('v')
                keyboard_controller.release('v')

        except sr.UnknownValueError:
            print(f"{current_model} could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from {current_model}; {e}")

# --- Hotkey Listener ---

def on_press(key):
    """Handles key press events for the hotkey."""
    global ctrl_press_timer, ctrl_key_pressed
    if key == keyboard.Key.ctrl_l and not is_recording and not ctrl_key_pressed:
        ctrl_key_pressed = True
        ctrl_press_timer = threading.Timer(2.0, start_recording)
        ctrl_press_timer.start()

def on_release(key):
    """Handles key release events for the hotkey."""
    global ctrl_press_timer, ctrl_key_pressed
    if key == keyboard.Key.ctrl_l:
        ctrl_key_pressed = False
        if ctrl_press_timer and ctrl_press_timer.is_alive():
            ctrl_press_timer.cancel()
        
        if is_recording:
            stop_recording_and_transcribe()

# --- System Tray Application ---

def toggle_recording():
    """Starts or stops recording based on the current state."""
    if is_recording:
        stop_recording_and_transcribe()
    else:
        start_recording()

def recording_text(item):
    """Dynamically sets the text for the recording menu item."""
    return "Stop recording" if is_recording else "Start recording"

def set_language(language_code):
    def on_set_language(icon, item):
        global current_language
        current_language = language_code
    return on_set_language

def is_language_selected(language_code):
    def on_is_selected(item):
        global current_language
        return current_language == language_code
    return on_is_selected

def open_about(icon, item):
    """Opens the GitHub repository in a web browser."""
    webbrowser.open("https://github.com/s-hubert/speech-to-text-win")

def create_tray_icon():
    """Creates and runs the system tray icon for the application."""
    global tray_icon, icon_red, icon_green, icon_yellow
    
    icon_red = create_image("red")
    icon_green = create_image("green")
    icon_yellow = create_image("yellow")

    language_menu = Menu(
        MenuItem('English', set_language('en'), checked=is_language_selected('en'), radio=True),
        MenuItem('German', set_language('de'), checked=is_language_selected('de'), radio=True),
        MenuItem('French', set_language('fr'), checked=is_language_selected('fr'), radio=True),
        MenuItem('Italian', set_language('it'), checked=is_language_selected('it'), radio=True)
    )

    model_menu = Menu(
        MenuItem('Faster Whisper (local)', set_model('faster_whisper'), checked=is_model_selected('faster_whisper'), radio=True),
        MenuItem('Google Speech Recognition API (online)', set_model('google'), checked=is_model_selected('google'), radio=True)
    )

    main_menu = Menu(
        MenuItem(recording_text, toggle_recording),
        MenuItem('Language', language_menu),
        MenuItem('Model', model_menu),
        MenuItem('About', open_about),
        MenuItem('Exit', on_exit)
    )

    tray_icon = Icon(
        "VoiceToText",
        icon_red,
        "Voice-to-Text",
        menu=main_menu
    )
    tray_icon.run()

def on_exit(icon, item):
    """Callback function to exit the application."""
    print("Exiting...")
    stop_event.set()
    listener.stop()
    icon.stop()

# --- Main Execution ---

if __name__ == "__main__":
    print("Voice-to-Text tool is running. Press and hold the left Ctrl key for 2 seconds to start recording.")
    print("Right-click the tray icon to exit.")

    # Start the keyboard listener in a separate thread
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # The main thread will run the system tray icon
    create_tray_icon()
