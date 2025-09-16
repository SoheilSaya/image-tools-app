@echo off
echo Installing dependencies...
python -m pip install -r requirements.txt

echo Building EXE...
pyinstaller app.spec

echo Done! Check dist folder for ImageTools.exe
pause
