@echo off
call venv\Scripts\activate.bat
echo Starting Django server...
python manage.py runserver 8000 --settings=travel_api.settings
pause