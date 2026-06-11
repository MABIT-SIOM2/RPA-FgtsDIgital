@echo off
chcp 65001 >nul
echo ========================================
echo   FGTS Digital - Build do Executavel
echo ========================================
echo.

REM Verificar se Python está disponível
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Python nao encontrado no PATH!
    echo Instale o Python 3.8+ e adicione ao PATH.
    pause
    exit /b 1
)

REM Verificar se PyInstaller está instalado
python -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo [ERRO] Falha ao instalar PyInstaller!
        pause
        exit /b 1
    )
)

REM 1. Limpar builds anteriores
echo [1/5] Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo OK - Limpeza concluida
echo.

REM 2. Instalar/atualizar dependencias
echo [2/5] Verificando dependencias...
pip install -r requirements.txt --quiet
echo OK - Dependencias verificadas
echo.

REM 3. Construir executavel
echo [3/5] Construindo executavel otimizado...
echo     Isso pode levar alguns minutos...
echo.
python -m PyInstaller --clean --noconfirm FgtsDigital.spec
echo.

REM 4. Verificar resultado
if exist "dist\FgtsDigital\FgtsDigital.exe" (
    echo OK - Executavel criado com sucesso!
    echo.
    echo [4/5] Informacoes do executavel:
    for %%F in ("dist\FgtsDigital\FgtsDigital.exe") do (
        echo     Arquivo: %%~nxF
        echo     Tamanho: %%~zF bytes
    )
    echo.
    echo [5/5] Criando pacote ZIP para distribuicao...
    powershell -Command "Compress-Archive -Path 'dist\FgtsDigital' -DestinationPath 'FgtsDigital_build.zip' -Force"
    if exist "FgtsDigital_build.zip" (
        echo OK - ZIP criado: FgtsDigital_build.zip
    ) else (
        echo AVISO - Nao foi possivel criar o ZIP (nao critico)
    )
    echo.
    echo ========================================
    echo   BUILD CONCLUIDO COM SUCESSO!
    echo ========================================
    echo.
    echo   Localizacao: dist\FgtsDigital\
    echo   Executavel:  dist\FgtsDigital\FgtsDigital.exe
    echo   ZIP:         FgtsDigital_build.zip
    echo.
    echo   Para distribuir: copie a pasta dist\FgtsDigital
    echo   inteira para a outra maquina e execute
    echo   FgtsDigital.exe
    echo.
    echo   NAO precisa instalar Python na outra maquina!
    echo ========================================
) else (
    echo.
    echo [ERRO] Falha ao criar executavel!
    echo Verifique os logs acima para mais detalhes.
    echo.
    echo Possiveis causas:
    echo   - Dependencia faltando (pip install -r requirements.txt)
    echo   - Erro de sintaxe no codigo Python
    echo   - Arquivo .spec com problema
)

echo.
pause
