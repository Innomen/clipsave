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
    with patch.object(clipsave.QFileDialog, 'getSaveFileName', return_value=(str(path), '')), patch.object(clipsave, 'copy_path', return_value=True) as saved_path:
        assert clipsave.run(app) == 0
    loaded = QImage(str(path))
    assert loaded.size() == image.size()
    assert loaded.pixelColor(0, 0) == image.pixelColor(0, 0)
    saved_path.assert_called_once_with(str(path))
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

with patch.dict(clipsave.os.environ, {'WAYLAND_DISPLAY': 'synthetic-test'}):
    with patch.object(clipsave.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as copy:
        assert clipsave.copy_path('/tmp/synthetic path.png')
        assert copy.call_args.args[0] == ['wl-copy', '--type', 'text/plain;charset=utf-8']
        assert copy.call_args.kwargs['input'] == b'/tmp/synthetic path.png'
    with patch.object(clipsave.subprocess, 'run', side_effect=FileNotFoundError):
        assert not clipsave.copy_path('/tmp/synthetic.png')
with tempfile.TemporaryDirectory() as tmp:
    app.clipboard().setImage(image)
    with patch.object(clipsave.QFileDialog, 'getSaveFileName', return_value=(str(Path(tmp) / 'image'), '')), \
         patch.object(clipsave, 'copy_path', return_value=False) as copy, \
         patch.object(clipsave.QMessageBox, 'warning') as warning:
        assert clipsave.run(app) == 0
        assert (Path(tmp) / 'image.png').exists()
        copy.assert_called_once_with(str(Path(tmp) / 'image.png'))
        warning.assert_called_once()
    with patch.object(clipsave.QFileDialog, 'getSaveFileName', return_value=('', '')), \
         patch.object(clipsave, 'copy_path') as copy:
        assert clipsave.run(app) == 0
        copy.assert_not_called()
print('PASS: persistent saved path, Wayland copy, appended extension, copy failure, cancel preserves clipboard')
