@echo off
:: instalar_plantillas.bat
:: Copia las plantillas Word al directorio de instalacion de AutoGeo.
:: Ejecutar en la maquina donde ya esta instalado AutoGeo.
chcp 65001 > nul

echo.
echo  ==========================================
echo    AutoGeo - Instalacion de Plantillas Word
echo  ==========================================
echo.

:: Ruta de instalacion (per-user, sin admin)
set "DEST=%LOCALAPPDATA%\Programs\AutoGeo\resources\backend\templates\word"

:: Si se instalo per-machine (con admin), probar tambien Program Files
if not exist "%DEST%" (
    set "DEST=%ProgramFiles%\AutoGeo\resources\backend\templates\word"
)

if not exist "%DEST%" (
    echo ERROR: No se encontro la carpeta de instalacion de AutoGeo.
    echo Verifica que AutoGeo este instalado correctamente.
    echo.
    pause
    exit /b 1
)

:: Carpeta origen de las plantillas (donde esta este script = raiz del proyecto)
set "SRC=%~dp0backend\templates\word"

if not exist "%SRC%" (
    echo ERROR: No se encontro la carpeta de plantillas en:
    echo %SRC%
    echo.
    echo Ejecuta este script desde la carpeta raiz del proyecto AutoGeo.
    pause
    exit /b 1
)

echo Origen:  %SRC%
echo Destino: %DEST%
echo.

:: Contar plantillas
set count=0
for /r "%SRC%" %%f in (*.docx *.doc *.dotx *.dot) do set /a count+=1
echo Plantillas encontradas: %count% archivos
echo.

if %count%==0 (
    echo No se encontraron archivos de plantilla (.docx, .doc, .dotx, .dot).
    pause
    exit /b 1
)

echo Copiando plantillas...
xcopy /E /I /Y /Q "%SRC%" "%DEST%"

if %errorlevel%==0 (
    echo.
    echo  ==========================================
    echo    PLANTILLAS INSTALADAS CORRECTAMENTE
    echo  ==========================================
    echo.
    echo  Las %count% plantillas estan listas en AutoGeo.
    echo  Abre AutoGeo para verificar.
) else (
    echo.
    echo ERROR: La copia fallo (codigo %errorlevel%).
    echo Intenta ejecutar como Administrador si tienes problemas de permisos.
)

echo.
pause
