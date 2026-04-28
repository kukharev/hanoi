from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

datas = []
binaries = []
hiddenimports = []

for mod in ['tkinter', '_tkinter']:
    hiddenimports += collect_submodules(mod)
    binaries += collect_dynamic_libs(mod)

datas += collect_data_files('tkinter')
datas += collect_data_files('tk')

a = Analysis(
    ['hanoi.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hook-runtime-tk.py'],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='hanoi',
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
    icon='hanoi.ico',
)
