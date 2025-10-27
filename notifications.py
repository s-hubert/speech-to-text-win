import threading
import config

def show_notification(message, title, timeout=None):
    """Shows a notification that disappears after a timeout."""
    if config.tray_icon:
        config.tray_icon.notify(message, title)
        if timeout:
            def remove():
                config.tray_icon.remove_notification()

            threading.Timer(timeout, remove).start()
