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
IF defined DEBUG (
	CD %JSPATH%
	CALL python -B %CLOSURE%\lib\closure\bin\build\depswriter.py --root_with_prefix=". ../js" > ..\goog\deps.js
) ELSE (
	CALL python -B %CLOSURE%\lib\closure\bin\build\closurebuilder.py --root=%CLOSURE%/ --root=%JSPATH%/ ^
		--namespace="HelloWorld" ^
		--output_mode=compiled ^
		--compiler_jar=%CLOSURE%\compiler.jar ^
		--compiler_flags="--js=%CLOSURE%/lib/closure/goog/deps.js" ^
		--compiler_flags="--compilation_level=ADVANCED_OPTIMIZATIONS" ^
		--compiler_flags="--externs=%JSPATH%\jquery.js" ^
		> %JSPATH%\compiled.js
)

PAUSE
