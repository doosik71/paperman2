@echo off

python --version >nul 2>&1

IF %ERRORLEVEL% NEQ 0 (
    call conda activate python
)

python manage.py runserver 8090
