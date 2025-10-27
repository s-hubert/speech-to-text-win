import webbrowser
from pystray import MenuItem, Icon, Menu
from PIL import Image, ImageDraw

import config
from recorder import start_recording, stop_recording_and_transcribe

def create_image(color):
    """Creates an icon image with a colored dot."""
    width, height = 64, 64
    background = "black"
    image = Image.new("RGB", (width, height), background)
    dc = ImageDraw.Draw(image)
    dc.ellipse([(10, 10), (width - 10, height - 10)], fill=color)
    return image

def toggle_recording():
    """Starts or stops recording based on the current state."""
    if config.is_recording:
        stop_recording_and_transcribe()
    else:
        start_recording()

def recording_text(item):
    """Dynamically sets the text for the recording menu item."""
    return "Stop recording" if config.is_recording else "Start recording"

def set_language(language_code):
    def on_set_language(icon, item):
        config.current_language = language_code
    return on_set_language

def is_language_selected(language_code):
    def on_is_selected(item):
        return config.current_language == language_code
    return on_is_selected

def set_model(model_name):
    def on_set_model(icon, item):
        config.current_model = model_name
    return on_set_model

def is_model_selected(model_name):
    def on_is_selected(item):
        return config.current_model == model_name
    return on_is_selected

def open_about(icon, item):
    """Opens the GitHub repository in a web browser."""
    webbrowser.open("https://github.com/s-hubert/speech-to-text-win")

def on_exit(icon, item):
    """Callback function to exit the application."""
    print("Exiting...")
    config.stop_event.set()
    if config.listener:
        config.listener.stop()
    icon.stop()

def create_tray_icon():
    """Creates and runs the system tray icon for the application."""
    config.icon_red = create_image("red")
    config.icon_green = create_image("green")
    config.icon_yellow = create_image("yellow")

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

    config.tray_icon = Icon(
        "Speech-To-Text",
        config.icon_red,
        "Voice-to-Text",
        menu=main_menu
    )
    config.tray_icon.run()
