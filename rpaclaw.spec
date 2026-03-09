# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for RPAclaw single-file executable."""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect data files from packages that have JSON/YAML/etc resources
litellm_datas = collect_data_files('litellm', include_py_files=False)
nanobot_datas = collect_data_files('nanobot', include_py_files=False)
tiktoken_datas = collect_data_files('tiktoken_ext', include_py_files=False)
certifi_datas = collect_data_files('certifi')

# Collect all submodules to avoid missing imports
litellm_imports = collect_submodules('litellm')
nanobot_imports = collect_submodules('nanobot')

a = Analysis(
    ['rpaclaw/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('rpaclaw/channels', 'rpaclaw/channels'),
    ] + litellm_datas + nanobot_datas + tiktoken_datas + certifi_datas,
    hiddenimports=[
        'rpaclaw',
        'rpaclaw.setup',
        'rpaclaw.chat',
        'rpaclaw.rpa_skill_creator',
        'rich',
        'rich.console',
        'rich.markdown',
        'rich.panel',
        'rich.prompt',
        'rich.table',
        'rich.spinner',
        'rich.live',
        'rich.text',
        'prompt_toolkit',
        'prompt_toolkit.history',
        'prompt_toolkit.key_binding',
        'prompt_toolkit.clipboard',
        'typer',
        'httpx',
        'httpx._transports',
        'loguru',
        'pydantic',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        'certifi',
    ] + litellm_imports + nanobot_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    a.datas,
    [],
    name='rpaclaw',
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
    icon=None,
)
