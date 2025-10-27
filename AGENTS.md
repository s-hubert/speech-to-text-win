# Project Context for AI Coding Assistants

This document provides context for AI coding assistants to understand the technical details of the "Speech-To-Text for Windows" project.

## Project Overview

This project is a Python-based Windows tray application that provides speech-to-text functionality. It allows the user to record their voice and have the transcribed text typed out at the current cursor position. The application is designed to be simple and hands-free.

The application is structured into the following modules:

-   `main.py`: The main entry point of the application.
-   `config.py`: Contains the application's configuration and global state.
-   `recorder.py`: Handles audio recording and transcription.
-   `hotkey.py`: Manages the global hotkey for recording.
-   `tray.py`: Manages the system tray icon and menu.

## Speech Recognition

The core speech recognition functionality is provided by the [`SpeechRecognition`](https://pypi.org/project/SpeechRecognition/) library. This library acts as a wrapper for various speech recognition engines and APIs.

The application allows the user to choose between two recognition models:

-   **Faster Whisper (local)**: This uses the `recognize_faster_whisper()` method for local, offline speech recognition. It is based on a reimplementation of OpenAI's Whisper model, optimized for speed. The "tiny" model is used.
-   **Google Speech Recognition API (online)**: This uses the `recognize_google()` method, which requires an internet connection.

### Language Support

The application supports multiple languages. The language can be selected from the tray icon menu. The supported languages and their corresponding codes are:

-   **English**: `en`
-   **German**: `de`
-   **French**: `fr`
-   **Italian**: `it`

The default language is determined by the user's system locale. The application handles the conversion of language codes to the format required by the selected speech recognition model.

## Dependencies

The project's dependencies are listed in the `requirements.txt` file. They can be installed using pip:

```bash
pip install -r requirements.txt
```

The key dependencies for speech recognition are:

-   `SpeechRecognition[faster-whisper]`: This installs the `SpeechRecognition` library along with the necessary extras for `faster-whisper`.
-   `soundfile`: This is required for reading audio files.
-   `pyaudio`: This is used for microphone input.