@echo off

python --version >nul 2>&1

IF %ERRORLEVEL% NEQ 0 (
    call conda activate python
)

echo Running at http://localhost:8090

python manage.py runserver 0.0.0.0:8090
