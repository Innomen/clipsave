import tempfile
from pathlib import Path
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QColor
import clipsave

app = QApplication([])
image = QImage(7, 5, QImage.Format.Format_ARGB32)
image.fill(QColor(10, 20, 30, 100))
app.clipboard().setImage(image)
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / 'saved.png'
    with patch.object(clipsave.QFileDialog, 'getSaveFileName', return_value=(str(path), '')):
        assert clipsave.run(app) == 0
    loaded = QImage(str(path))
    assert loaded.size() == image.size()
    assert loaded.pixelColor(0, 0) == image.pixelColor(0, 0)
    assert app.clipboard().image().pixelColor(0, 0) == image.pixelColor(0, 0)
    with patch.object(clipsave.QFileDialog, 'getSaveFileName', return_value=('', '')):
        assert clipsave.run(app) == 0
    assert not clipsave.save_png(image, Path(tmp) / 'missing' / 'image.png')
    app.clipboard().clear()
    with patch.object(clipsave.QMessageBox, 'information') as message:
        assert clipsave.run(app) == 1
        message.assert_called_once()
print('PASS: clipboard → dialog → PNG, alpha, cancel, write failure, empty clipboard')
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
import subprocess
encoded = QByteArray()
buffer = QBuffer(encoded)
buffer.open(QIODevice.OpenModeFlag.WriteOnly)
assert image.save(buffer, 'PNG')
with patch.dict(clipsave.os.environ, {'WAYLAND_DISPLAY': 'synthetic-test'}):
    with patch.object(clipsave.subprocess, 'run', side_effect=[
        subprocess.CompletedProcess([], 0, b'text/plain\nimage/png\n', b''),
        subprocess.CompletedProcess([], 0, bytes(encoded), b'')]):
        assert clipsave.clipboard_image(app).pixelColor(0, 0) == image.pixelColor(0, 0)
    with patch.object(clipsave.subprocess, 'run', side_effect=subprocess.TimeoutExpired('wl-paste', 5)):
        assert clipsave.clipboard_image(app).isNull()
print('PASS: Wayland MIME selection, PNG decoding, bounded clipboard timeout')
