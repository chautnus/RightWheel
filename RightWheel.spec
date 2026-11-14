# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('assets/icon.png', 'assets')],
    hiddenimports=[
        'pystray._win32',   # pystray backend is loaded dynamically
        'PIL.Image',
        'PIL.ImageDraw',
        'tkinter',
        'tkinter.simpledialog',
        'tkinter.filedialog',
        '_tkinter',
        # urllib.request deps (needed for LemonSqueezy API calls)
        'email', 'email.message', 'email.parser', 'email.headerregistry',
        'email.contentmanager', 'email.generator', 'email.utils',
        'http', 'http.client',
        'html', 'html.parser',
        # i18n locale modules (loaded dynamically via importlib)
        'features.i18n.en', 'features.i18n.fr', 'features.i18n.pt',
        'features.i18n.es', 'features.i18n.it', 'features.i18n.vi',
        'features.i18n.id', 'features.i18n.th', 'features.i18n.zh',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # stdlib bloat
        'unittest', 'xml', 'xmlrpc', 'pydoc', 'doctest', 'difflib', 'pdb',
        'test', 'tests', 'lib2to3', 'tkinter.test', 'distutils',
        'multiprocessing', 'concurrent', 'asyncio',
        # heavy scientific libs pulled in by PIL (not needed — app only loads icon PNG)
        'numpy', 'numpy.core', 'numpy.lib', 'numpy.linalg', 'numpy.fft',
        'numpy.random', 'numpy.polynomial', 'numpy.ma', 'numpy.matrixlib',
        'scipy', 'pandas', 'matplotlib', 'IPython', 'PIL.ImageMath',
        # other unused
        'cryptography', 'OpenSSL', 'Crypto',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RightWheel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # no console window — tray app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
)
