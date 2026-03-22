# -*- mode: python ; coding: utf-8 -*-
import os
import importlib

# selenium 전체 하위 모듈 수집
selenium_hidden = []
import selenium
sel_root = os.path.dirname(selenium.__file__)
for root, dirs, files in os.walk(sel_root):
    for f in files:
        if f.endswith('.py') and f != '__init__.py':
            rel = os.path.relpath(os.path.join(root, f), os.path.dirname(sel_root))
            mod = rel.replace(os.sep, '.').replace('.py', '')
            selenium_hidden.append(mod)

a = Analysis(
    ['macro.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        # selenium 핵심 모듈
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.webdriver',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.common',
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.keys',
        'selenium.webdriver.common.action_chains',
        'selenium.webdriver.common.options',
        'selenium.webdriver.common.service',
        'selenium.webdriver.common.driver_finder',
        'selenium.webdriver.common.selenium_manager',
        'selenium.webdriver.remote',
        'selenium.webdriver.remote.webdriver',
        'selenium.webdriver.remote.webelement',
        'selenium.webdriver.remote.remote_connection',
        'selenium.webdriver.remote.command',
        'selenium.webdriver.remote.errorhandler',
        'selenium.common',
        'selenium.common.exceptions',
        # ddddocr
        'ddddocr',
        'onnxruntime',
        'cv2',
        'PIL',
        'PIL.Image',
    ] + selenium_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# ddddocr 데이터 파일 수집
import ddddocr as _ddddocr
ddddocr_dir = os.path.dirname(_ddddocr.__file__)
for f in os.listdir(ddddocr_dir):
    fpath = os.path.join(ddddocr_dir, f)
    if os.path.isfile(fpath) and not f.endswith('.py') and not f.endswith('.pyc'):
        a.datas.append((os.path.join('ddddocr', f), fpath, 'DATA'))

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='인터파크좌석매크로',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)
