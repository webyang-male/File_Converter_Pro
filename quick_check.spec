# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — Quick Check
# pyright: reportUndefinedVariable=false

block_cipher = None

a = Analysis(
    ['quick_check.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # All GUIs (keep tkinter)
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6',

        # Science / ML
        'torch', 'torchvision', 'tensorflow',
        'numpy', 'pandas', 'scipy', 'sklearn',
        'matplotlib', 'PIL', 'cv2', 'easyocr',

        # Networking / web
        'requests', 'urllib3', 'http', 'email',
        'ftplib', 'imaplib', 'smtplib', 'poplib',

        # Crypto
        'cryptography', 'ssl', '_ssl',

        # Stdlib modules not used
        'xml', 'xmlrpc', 'pydoc', 'doctest',
        'unittest', 'distutils', 'setuptools',
        'multiprocessing', 'concurrent',
        'asyncio', 'zipimport',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    target_arch='x86_64',
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Quick Check',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'python3.dll',
        'python313.dll',
    ],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon='icon.ico',
)
