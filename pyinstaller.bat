REM use pyinstaller vs osnap since we want a single command line executable
rmdir /s /q build
rmdir /s /q dist
venv\Scripts\pyinstaller.exe -F compare_dirs\compare_dirs.py
