# Project Context for AI Coding Assistants

This document provides context for AI coding assistants to understand the technical details of the "Speech-To-Text for Windows" project.

## Project Overview

This project is a Python-based Windows tray application that provides speech-to-text functionality. It allows the user to record their voice and have the transcribed text typed out at the current cursor position. The application is designed to be simple and hands-free.

## Speech Recognition

The core speech recognition functionality is provided by the [`SpeechRecognition`](https://pypi.org/project/SpeechRecognition/) library. This library acts as a wrapper for various speech recognition engines and APIs.

### Recognizer: Faster Whisper

This project uses the **Faster Whisper** recognizer through the `recognize_faster_whisper()` method provided by the `SpeechRecognition` library. Faster Whisper is a reimplementation of OpenAI's Whisper model that is optimized for speed and efficiency, especially on CPUs.

The "tiny" model is used to provide a good balance between performance and accuracy.

### Language Support

The application supports multiple languages. The language can be selected from the tray icon menu. The supported languages and their corresponding codes are:

-   **English**: `en`
-   **German**: `de`
-   **French**: `fr`
-   **Italian**: `it`

The default language is determined by the user's system locale.

## Dependencies

The project's dependencies are listed in the `requirements.txt` file. They can be installed using pip:

```bash
pip install -r requirements.txt
```

The key dependencies for speech recognition are:

-   `SpeechRecognition[faster-whisper]`: This installs the `SpeechRecognition` library along with the necessary extras for `faster-whisper`.
-   `soundfile`: This is required for reading audio files.
-   `pyaudio`: This is used for microphone input.

By using `SpeechRecognition[faster-whisper]`, the installation process handles the setup of `faster-whisper` and its dependencies.
