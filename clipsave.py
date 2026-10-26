#!/usr/bin/python3
"""Save a snapshot of the clipboard image through a native Save As dialog."""
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime

from PyQt6.QtCore import QIODevice, QSaveFile, QStandardPaths
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox


def clipboard_image(app):
    # wl-paste can read the selection before our window has keyboard focus.
    if os.environ.get('WAYLAND_DISPLAY'):
        try:
            result = subprocess.run(['wl-paste', '--list-types'], capture_output=True, timeout=5)
            types = result.stdout.decode('utf-8', errors='replace').splitlines()
            images = [t for t in types if t.startswith('image/')]
            images.sort(key=lambda t: t != 'image/png')
            for mime in images:
                data = subprocess.run(['wl-paste', '--no-newline', '--type', mime],
                                      capture_output=True, timeout=10)
                if data.returncode == 0:
                    image = QImage.fromData(data.stdout)
                    if not image.isNull():
                        return image
        except (OSError, subprocess.TimeoutExpired):
            pass
        return QImage()
    return app.clipboard().image().copy()


def save_png(image, path):
    """Atomic replacement: a failed write cannot truncate an existing image."""
    output = QSaveFile(str(path))
    if not output.open(QIODevice.OpenModeFlag.WriteOnly):
        return False
    if not image.save(output, 'PNG'):
        output.cancelWriting()
        return False
    return output.commit()


def run(app):
    image = clipboard_image(app)
    if image.isNull():
        QMessageBox.information(None, 'ClipSave',
                                'No image in the clipboard. Copy an image, then launch ClipSave again.')
        return 1
    folder = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)
    name = 'clipboard-' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f') + '.png'
    while True:
        path, _ = QFileDialog.getSaveFileName(None, 'Save clipboard image',
                                             str(Path(folder or str(Path.home())) / name),
                                             'PNG image (*.png)')
        if not path:
            return 0
        # Enforce PNG extension without silently overwriting a different filename.
        if not path.lower().endswith('.png'):
            path += '.png'
            if Path(path).exists() and QMessageBox.question(
                None, 'ClipSave', 'The PNG file already exists. Replace it?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                continue
        if save_png(image, path):
            return 0
        QMessageBox.warning(None, 'ClipSave',
                            'Could not save the image. Choose a writable location and try again.')


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('ClipSave')
    app.setDesktopFileName('clipsave')
    return run(app)


if __name__ == '__main__':
    sys.exit(main())
