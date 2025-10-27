# Speech-To-Text for Windows

This is a simple Windows tray application that converts your speech to text. It uses the `speech_recognition` library to listen to your microphone and the `keyboard` library to type the recognized text.

## Purpose

The main purpose of this application is to provide a simple, hands-free way to type on a Windows machine. This can be useful for people who have difficulty typing, or for anyone who wants to be more productive.

## Usage

1.  Run the application. A new icon will appear in your system tray.
2.  Click the tray icon to toggle the listening state.
3.  When the icon is green, the application is listening for your voice.
4.  When the icon is red, the application is not listening.
5.  The recognized text will be typed wherever your cursor is focused.
6.  Right-click the tray icon and select "Exit" to close the application.

## Installation

To install the dependencies, follow these steps:

1.  Open your command line or terminal.
2.  Navigate to the script's directory: `cd speech-to-text`
3.  You can temporarily allow scripts for your current session, which is a safe and recommended approach. Run this command in your PowerShell terminal:
    `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
4.  (Recommended) Create and activate a virtual environment to keep your project dependencies isolated:

    ```
    python -m venv venv
    .\venv\Scripts\activate
    ```

5.  Install the requirements: `pip install -r requirements.txt`

Install using: `pyinstaller --noconsole --onefile --windowed speech_to_text.py`
