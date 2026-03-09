# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for RPAclaw single-file executable."""

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['rpaclaw/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('rpaclaw/channels', 'rpaclaw/channels'),
    ],
    hiddenimports=[
        'nanobot',
        'nanobot.agent',
        'nanobot.agent.loop',
        'nanobot.agent.tools',
        'nanobot.bus',
        'nanobot.bus.queue',
        'nanobot.cli',
        'nanobot.cli.commands',
        'nanobot.config',
        'nanobot.config.loader',
        'nanobot.config.schema',
        'nanobot.cron',
        'nanobot.cron.service',
        'rpaclaw',
        'rpaclaw.setup',
        'rpaclaw.chat',
        'rpaclaw.rpa_skill_creator',
        'rich',
        'rich.console',
        'rich.markdown',
        'rich.panel',
        'rich.prompt',
        'prompt_toolkit',
        'typer',
        'httpx',
        'loguru',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
    ],
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
