@ECHO OFF
SET PYTHONPATH=%~dp0\..\server
SET APP_ROUTE=%PYTHONPATH%\handler
SET FILE_PATH=%~dp0\..\website

python -B %PYTHONPATH%\tarantula.py -a %APP_ROUTE% -f %FILE_PATH% -d True

PAUSE
