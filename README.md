To install the dependencies, follow these steps:

1. Open your command line or terminal.
2. Navigate to the script's directory: `cd speech-to-text`
3. You can temporarily allow scripts for your current session, which is a safe and recommended approach. Run this command in your PowerShell terminal:
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
4. (Recommended) Create and activate a virtual environment to keep your project dependencies isolated:

```
python -m venv venv
.\venv\Scripts\activate
```

5. Install the requirements: `pip install -r requirements.txt`

Install using: `pyinstaller --noconsole --onefile --windowed speech_to_text.py`
