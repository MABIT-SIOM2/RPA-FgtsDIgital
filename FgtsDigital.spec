# -*- mode: python ; coding: utf-8 -*-
# FgtsDigital.spec - Configuração otimizada do PyInstaller
# Gera um executável standalone com todas as dependências embutidas.

import os

block_cipher = None

a = Analysis(
    ['gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Assets de imagem usados pela automação (pyautogui locateOnScreen)
        ('src/assets/site/*.png', 'src/assets/site'),
        ('src/assets/arquivo/*.png', 'src/assets/arquivo'),
        ('src/assets/dominio', 'src/assets/dominio'),
        ('src/assets/onvio', 'src/assets/onvio'),
        # Webapp (Flask templates + static files)
        ('webapp/templates', 'webapp/templates'),
        ('webapp/static', 'webapp/static'),
        # Arquivo de configuração padrão (copiado para _internal; em runtime buscamos nos dois locais)
        ('config_multi.json', '.'),
    ],
    hiddenimports=[
        # Core da aplicação
        'src',
        'src.bot_pyautogui',
        'src.utils.automation',
        'src.utils.excel_handler',
        'src.utils.database_handler',
        'src.utils.captcha_cutter',
        'src.services.browser',
        'src.services.fgts_digital_site',
        'src.services.captcha_solver',
        # Webapp
        'webapp.app',
        # Dependências externas
        'openpyxl',
        'pyautogui',
        'pyperclip',
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        'pandas',
        'pandas._libs',
        'pandas._libs.tslibs',
        'numpy',
        'mysql.connector',
        'mysql.connector.plugins',
        'mysql.connector.plugins.caching_sha2_password',
        'mysql.connector.plugins.mysql_native_password',
        'flask',
        'flask_cors',
        'fpdf',
        'fpdf.enums',
        'cv2',
        'pygetwindow',
        'pyscreeze',
        'mouseinfo',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclui módulos pesados e desnecessários para reduzir tamanho
        'matplotlib',
        'scipy',
        'sklearn',
        'torch',
        'tensorflow',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
        'xmlrpc',
        'lib2to3',
        'ensurepip',
        'venv',
        'tkinter.test',
        'idlelib',
        'turtledemo',
        'asyncio.test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FgtsDigital',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprime binários com UPX (se disponível)
    console=False,  # Sem janela de console (GUI pura)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FgtsDigital',
)
