# Speech-To-Text for Windows

This is a simple Windows tray application that converts your speech to text. It uses the `speech_recognition` library to listen to your microphone and the `keyboard` library to type the recognized text.

## Purpose

The main purpose of this application is to provide a simple, hands-free way to type on a Windows machine. This can be useful for people who have difficulty typing, or for anyone who wants to be more productive.

## Usage

1. Run the application by executing the `main.py` script: `python main.py`. A new icon will appear in your system tray.
2. Click the tray icon to toggle the listening state.
3. When the icon is green, the application is listening for your voice.
4. When the icon is yellow, the application is transcribing your voice.
5. When the icon is red, the application is not listening.
6. The recognized text will be typed wherever your cursor is focused.
7. Right-click the tray icon to access the menu, where you can change the language, the recognition model, and exit the application.

The application allows the user to choose between two recognition models:

- **Whisper (local)**: This uses the `recognize_whisper()` method, which requires an internet connection to download the `turbo` model locally upon first use. [docs](https://raw.githubusercontent.com/openai/whisper/refs/heads/main/README.md)
- **Faster Whisper (local)**: This uses the `recognize_faster_whisper()` method for local, offline speech recognition. It is based on a reimplementation of OpenAI's Whisper model, optimized for speed. The "tiny" model is used. [docs](https://raw.githubusercontent.com/SYSTRAN/faster-whisper/refs/heads/master/README.md)
- **Google Speech Recognition API (online)**: This uses the `recognize_google()` method, which requires an internet connection. [docs](https://cloud.google.com/speech-to-text/docs/reference/rest)

The application supports multiple languages. The language can be selected from the tray icon menu. The supported languages and their corresponding codes are:

- **English**: `en`
- **German**: `de`
- **French**: `fr`
- **Italian**: `it`

## Installation

To install the dependencies, follow these steps:

1. Open your command line or terminal.
2. Navigate to the script's directory.
3. You can temporarily allow scripts for your current session, which is a safe and recommended approach. Run this command in your PowerShell terminal:
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
4. (Recommended) Create and activate a virtual environment to keep your project dependencies isolated:

   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```

5. Install the requirements: `pip install -r requirements.txt`

To create a standalone executable, you can use `pyinstaller`:

```
pyinstaller --noconsole --onefile --windowed --name SpeechToTextWin main.py
```

This will create a single executable file in the `dist` folder.
