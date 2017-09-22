@ECHO OFF
SET CLOSURE=%~dp0\..\closure
SET TSPATH=%~dp0\..\client
SET JSPATH=%~dp0\..\website\js
SET GOOGPATH=%~dp0\..\website\goog
SET DEBUG=True

CALL tsc --outDir %JSPATH% --project %TSPATH%

MD %GOOGPATH%
COPY %CLOSURE%\lib\closure\goog\base.js %GOOGPATH%\
COPY %TSPATH%\lib\jquery\jquery-3.2.1.min.js %JSPATH%\jquery.js
CD %JSPATH%
IF defined DEBUG (
	CALL python -B %CLOSURE%\lib\closure\bin\build\depswriter.py --root_with_prefix=". ../js" > ..\goog\deps.js
) ELSE (
	ECHO No release build!
)

PAUSE
