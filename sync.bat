@echo off
chcp 65001 > NUL
echo ===================================================
echo 🌙 סנכרון אימוני Garmin Connect למירוץ הלילה 2026
echo ===================================================
echo.
python -X utf8 sync_garmin.py --deploy
echo.
pause
