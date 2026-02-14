@echo off
echo ========================================
echo  Construindo RoboSocietario Executavel
echo ========================================
echo.

REM Limpar builds anteriores
echo [1/4] Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo ✓ Limpeza concluida
echo.

REM Construir executavel
echo [2/4] Construindo executavel otimizado...
python -m PyInstaller --clean BotSocietario.spec
echo.

REM Verificar se foi criado com sucesso
if exist "dist\RoboSocietario\RoboSocietario.exe" (
    echo ✓ Executavel criado com sucesso!
    echo.
    echo [3/4] Informacoes do executavel:
    dir "dist\RoboSocietario\RoboSocietario.exe"
    echo.
    echo [4/4] Localizacao: dist\RoboSocietario\
    echo.
    echo ========================================
    echo  BUILD CONCLUIDO COM SUCESSO!
    echo ========================================
) else (
    echo ✗ Erro ao criar executavel
    echo Verifique os logs acima para mais detalhes
    pause
    exit /b 1
)

pause
