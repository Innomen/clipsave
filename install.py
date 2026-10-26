#!/usr/bin/python3
"""Idempotent per-user installation, with no root access required."""
import os
from pathlib import Path
import shlex
import shutil
import subprocess

source = Path(__file__).resolve().parent
home = Path.home()
base = Path(os.environ.get('XDG_DATA_HOME', home / '.local/share'))
apps = base / 'applications'
bin_dir = home / '.local/bin'
apps.mkdir(parents=True, exist_ok=True)
bin_dir.mkdir(parents=True, exist_ok=True)
launcher = bin_dir / 'clipsave'
launcher.write_text('#!/bin/sh\nexec /usr/bin/python3 ' + shlex.quote(str(source / 'clipsave.py')) + ' "$@"\n')
launcher.chmod(0o755)
# Desktop Exec has its own quoting rules, separate from shell quoting.
quoted = '"' + str(launcher).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%') + '"'
(apps / 'clipsave.desktop').write_text(
    '[Desktop Entry]\nType=Application\nName=ClipSave\nComment=Save the clipboard image as a PNG file\n'
    f'Exec={quoted}\nIcon=edit-paste\nTerminal=false\nCategories=Graphics;\n'
    'Keywords=clipboard;image;save;png;\nStartupNotify=false\n')
for program in ('update-desktop-database', 'kbuildsycoca6'):
    if shutil.which(program):
        subprocess.run([program, str(apps)] if program == 'update-desktop-database' else [program, '--noincremental'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('ClipSave installed in the application menu.')
