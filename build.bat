@echo off
echo Creating icon...
python create_icon.py
echo Building executable...
python build_exe.py
echo Done!
pause 