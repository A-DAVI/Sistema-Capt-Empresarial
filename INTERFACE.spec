# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['INTERFACE.py'],
    pathex=[os.path.abspath('.')], 
    binaries=[],
    datas=[
        ('app', 'app'),
        ('relatorios', 'relatorios'),
        ('logo_empresa.png', '.'),
        ('logo.ico', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'requests',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL._imaging',              # >>> IMPORTANTE
        'PIL._tkinter_finder',       # >>> IMPORTANTE
        'CTkMessagebox',
        'reportlab',
        'dotenv',            # python-dotenv para carregar .env no executável
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

env_file = os.path.join(os.path.abspath('.'), '.env')
if os.path.exists(env_file):
    a.datas.append((env_file, '.', 'DATA'))

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CentralDeControle-GRUPO14D',          # <<< sem acento!
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,             # janela oculta
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico',
    uac_admin=True,            # solicita elevação ao iniciar
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='INTERFACE'
)
