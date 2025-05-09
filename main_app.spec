# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_app.py'],
    pathex=[],
    binaries=[],
    datas=[('E:\\\\Project_AI\\\\itsOji_eyeq_enterprise_28_04_25\\\\itsOji_eyeq_enterprise\\\\ui\\\\assets', 'ui\\\\assets'), ('E:\\\\Project_AI\\\\itsOji_eyeq_enterprise_28_04_25\\\\itsOji_eyeq_enterprise\\\\ui\\\\styles', 'ui\\\\styles'), ('E:\\\\Project_AI\\\\itsOji_eyeq_enterprise_28_04_25\\\\itsOji_eyeq_enterprise\\\\config', 'config')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='main_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
