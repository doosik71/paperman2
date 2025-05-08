@echo off

cd %~dp0
call %~dp0\.venv\Scripts\activate

echo Running at http://localhost:8090

python manage.py runserver 0.0.0.0:8090
