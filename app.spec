# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Vazir-Bold.ttf', 'fonts'),
        ('Vazir-Medium.ttf', 'fonts'),
        ('Vazir-Regular.ttf', 'fonts'),
        ('Vazir-Black.ttf', 'fonts'),
        ('Vazir-Light.ttf', 'fonts'),
        ('Vazir-Thin.ttf', 'fonts'),
        ('Vazir-Variable.ttf', 'fonts'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PIL.Image',
        'PIL.ImageDraw', 
        'PIL.ImageFont',
        'reportlab.pdfgen.canvas',
        'reportlab.lib.units',
        'arabic_reshaper',
        'bidi.algorithm',
        'bidi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageTools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
