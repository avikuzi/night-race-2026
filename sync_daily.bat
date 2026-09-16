@echo off
chcp 65001 > NUL
set PATH=C:\Users\aviku\AppData\Local\Programs\Python\Python312;C:\Users\aviku\AppData\Roaming\npm;C:\Program Files\nodejs;%PATH%
cd /d "%~dp0"
echo [%date% %time%] Running Garmin sync... >> sync_daily.log
python -X utf8 sync_garmin.py --deploy >> sync_daily.log 2>&1
echo [%date% %time%] Sync finished with exit code %errorlevel% >> sync_daily.log
