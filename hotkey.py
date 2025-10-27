import threading
from pynput import keyboard

import config
from recorder import start_recording, stop_recording_and_transcribe

def on_press(key):
    """Handles key press events for the hotkey."""
    if key == keyboard.Key.ctrl_l and not config.is_recording and not config.ctrl_key_pressed:
        config.ctrl_key_pressed = True
        config.ctrl_press_timer = threading.Timer(2.0, start_recording)
        config.ctrl_press_timer.start()

def on_release(key):
    """Handles key release events for the hotkey."""
    if key == keyboard.Key.ctrl_l:
        config.ctrl_key_pressed = False
        if config.ctrl_press_timer and config.ctrl_press_timer.is_alive():
            config.ctrl_press_timer.cancel()
        
        if config.is_recording:
            stop_recording_and_transcribe()

def listen_for_hotkey():
    """Starts the keyboard listener in a separate thread."""
    config.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    config.listener.start()
