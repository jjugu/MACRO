# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = []
datas += collect_data_files('ddddocr')


a = Analysis(
    ['macro.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['selenium.webdriver.chrome.webdriver', 'selenium.webdriver.chrome.service', 'selenium.webdriver.chrome.options', 'selenium.webdriver.common.by', 'selenium.webdriver.common.keys', 'selenium.webdriver.common.service', 'selenium.webdriver.common.options', 'selenium.webdriver.common.driver_finder', 'selenium.webdriver.common.selenium_manager', 'selenium.webdriver.remote.webdriver', 'selenium.webdriver.remote.webelement', 'selenium.webdriver.remote.remote_connection', 'selenium.webdriver.remote.command', 'selenium.webdriver.remote.errorhandler', 'selenium.common.exceptions', 'ddddocr', 'onnxruntime', 'PIL', 'PIL.Image'],
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
    name='인터파크좌석매크로_debug',
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
