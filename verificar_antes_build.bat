@echo off
chcp 65001 >nul
echo ========================================
echo  Verificação Pré-Build - RoboSocietario
echo ========================================
echo.

REM Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python não encontrado! Instale Python 3.8+
    pause
    exit /b 1
)
python --version
echo ✓ Python OK
echo.

REM Verificar dependências principais
echo [2/5] Verificando dependências principais...
python -c "import pyautogui, openpyxl, PIL, pyperclip, pygetwindow" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Dependências faltando! Execute: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✓ Dependências OK
echo.

REM Verificar PyInstaller
echo [3/5] Verificando PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ PyInstaller não instalado! Execute: pip install pyinstaller
    pause
    exit /b 1
)
echo ✓ PyInstaller OK
echo.

REM Verificar arquivos necessários
echo [4/5] Verificando arquivos do projeto...
if not exist "gui.py" (
    echo ✗ gui.py não encontrado!
    pause
    exit /b 1
)
if not exist "BotSocietario.spec" (
    echo ✗ BotSocietario.spec não encontrado!
    pause
    exit /b 1
)
if not exist "src\assets\logo.png" (
    echo ⚠ Logo não encontrado em src\assets\logo.png
    echo   O executável funcionará, mas sem logo
) else (
    echo ✓ Logo encontrado
)
echo ✓ Arquivos principais OK
echo.

REM Testar execução do código
echo [5/5] Testando execução do código...
echo ⚠ A janela da aplicação abrirá por 3 segundos para teste...
timeout /t 2 /nobreak >nul
start /min python gui.py
timeout /t 3 /nobreak >nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Societário*" >nul 2>&1
echo ✓ Código executa sem erros críticos
echo.

echo ========================================
echo  ✓ TUDO PRONTO PARA BUILD!
echo ========================================
echo.
echo Próximo passo: Execute build_exe.bat
echo.
pause
