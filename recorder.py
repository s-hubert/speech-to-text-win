import threading
import wave
import winsound
import speech_recognition as sr
import pyaudio
from pynput.keyboard import Controller as KeyboardController
from pynput import keyboard
import ctypes

import config
import notifications

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

def start_recording():
    """Initializes and starts the audio recording stream."""
    if config.is_recording:
        return

    notifications.show_notification("Recording started...", title="Speech-To-Text")

    if config.tray_icon:
        config.tray_icon.icon = config.icon_green
    
    winsound.Beep(1000, 200)

    print("Starting recording...")
    config.is_recording = True
    config.audio_frames = []
    config.p = pyaudio.PyAudio()
    config.stream = config.p.open(format=config.FORMAT,
                    channels=config.CHANNELS,
                    rate=config.RATE,
                    input=True,
                    frames_per_buffer=config.CHUNK)
    
    # Recording loop runs in a separate thread
    threading.Thread(target=record_loop).start()

def record_loop():
    """Continuously records audio chunks until recording is stopped."""
    while config.is_recording:
        try:
            data = config.stream.read(config.CHUNK)
            config.audio_frames.append(data)
        except IOError:
            # This can happen if the stream is closed while reading
            break

def stop_recording_and_transcribe():
    """Stops recording, saves the audio, and initiates transcription."""
    if not config.is_recording:
        return

    if config.tray_icon:
        config.tray_icon.icon = config.icon_yellow

    print("Stopping recording...")
    config.is_recording = False
    
    # Allow the recording loop to finish
    threading.Timer(0.1, _finish_processing).start()

def _finish_processing():
    """Saves audio to a file and transcribes it."""
    config.stream.stop_stream()
    config.stream.close()
    config.p.terminate()

    # Save the recorded data as a WAV file
    with wave.open(config.RECORDING_FILENAME, 'wb') as wf:
        wf.setnchannels(config.CHANNELS)
        wf.setsampwidth(config.p.get_sample_size(config.FORMAT))
        wf.setframerate(config.RATE)
        wf.writeframes(b''.join(config.audio_frames))

    print("Audio saved. Transcribing...")
    transcribe_audio(config.RECORDING_FILENAME)
    notifications.close_notification()

    if config.tray_icon:
        config.tray_icon.icon = config.icon_red

def transcribe_audio(filename):
    """Converts audio file to text and types it."""
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        r.adjust_for_ambient_noise(source)
        audio_data = r.record(source)
        try:
            if config.current_model == "faster_whisper":
                # Using Faster Whisper on CPU
                text = r.recognize_faster_whisper(audio_data, model="tiny", language=config.current_language, init_options={"device": "cpu"})
                print(f"Recognized with Faster Whisper: {text}")
            else: # google
                google_language_map = {
                    'en': 'en-US',
                    'de': 'de-DE',
                    'fr': 'fr-FR',
                    'it': 'it-IT'
                }
                google_language = google_language_map.get(config.current_language, 'en-US')
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
            print(f"{config.current_model} could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from {config.current_model}; {e}")
