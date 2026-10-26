# ClipSave

Copy an image, launch **ClipSave** from the application menu, choose a filename and folder, and save. The default is a timestamped PNG in Pictures. Cancel leaves everything untouched. Clipboard contents stay on your machine and are never changed by ClipSave.

A small KDE-friendly Linux utility using the native Qt Save As dialog. Works with Wayland through `wl-paste` and X11 through Qt. Transparent images stay transparent. Writes are atomic, overwrite confirmation is enabled, and failed saves let you choose another location.

## Install

Requires Python 3, PyQt6, and, on Wayland, wl-clipboard. On Arch/Garuda:

```sh
sudo pacman -S python-pyqt6 wl-clipboard
```

From this directory:

```sh
/usr/bin/python3 install.py
```

Keep this directory in place: the installed launcher points to it. Run the installer again after moving it. No background service, clipboard history, network requests, or telemetry. To remove the menu entry and command, delete `~/.local/share/applications/clipsave.desktop` and `~/.local/bin/clipsave`.

## Test

Synthetic clipboard only, on an isolated display:

```sh
env -u WAYLAND_DISPLAY QT_QPA_PLATFORM=xcb xvfb-run -a /usr/bin/python3 test_clipsave.py
```

## Related tools

[Clipboard to File](https://github.com/costales/clipboard-to-file) provides Nautilus/Nemo/Caja context menus. [ctrl-chris/clipsave](https://github.com/ctrl-chris/clipsave) is a browser extension. This utility provides a standalone Linux application-menu action.
