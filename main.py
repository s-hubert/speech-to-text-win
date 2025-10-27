from hotkey import listen_for_hotkey
from tray import create_tray_icon
import logging
import os
import config


def setup_logging():
    """Remove existing log file and configure Python logging to write to the app log."""
    log_path = config.get_log_path()
    try:
        if log_path.exists():
            log_path.unlink()
    except Exception:
        # If we cannot remove the old log, continue and append to it
        pass

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


if __name__ == "__main__":
    setup_logging()
    logging.info("Voice-to-Text tool starting")
    print("Voice-to-Text tool is running. Press and hold the left Ctrl key for 2 seconds to start recording.")
    print("Right-click the tray icon to exit.")

    listen_for_hotkey()
    create_tray_icon()
    logging.info("Voice-to-Text tool exiting")
