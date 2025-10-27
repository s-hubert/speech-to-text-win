from hotkey import listen_for_hotkey
from tray import create_tray_icon

if __name__ == "__main__":
    print("Voice-to-Text tool is running. Press and hold the left Ctrl key for 2 seconds to start recording.")
    print("Right-click the tray icon to exit.")

    listen_for_hotkey()
    create_tray_icon()
