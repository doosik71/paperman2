@echo off

cd %~dp0
call %~dp0\.venv\Scripts\activate

where python

echo Running at https://localhost:8090

rem python manage.py runserver 0.0.0.0:8090
python manage.py runsslserver 0.0.0.0:8090 --certificate localhost.pem --key localhost-key.pem

pause