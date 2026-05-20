# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Program Files\\Python314\\Lib\\site-packages\\customtkinter', 'customtkinter'), ('assets', 'assets'), ('smac_station.db', '.'), ('config.py', '.')],
    hiddenimports=['customtkinter', 'psutil', 'sounddevice', 'soundfile', 'librosa', 'pygame', 'gtts', 'pydub', 'sqlite3', 'PIL', 'pyttsx3', 'pyttsx3.drivers', 'pyttsx3.drivers.sapi5', 'pyttsx3.drivers.dummy', 'win32com', 'win32com.client', 'comtypes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SMAC_Broadcast_Station',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SMAC_Broadcast_Station',
)
