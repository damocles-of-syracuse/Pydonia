from PyQt6 import QtCore

# Create an event filter object to watch for content resize events and recompute
class ResizeWatcher(QtCore.QObject):
    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self._callback = callback

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.Resize:
            # delay slightly to ensure layouts have updated geometry
            QtCore.QTimer.singleShot(0, self._callback)
        return False

'''watcher = ResizeWatcher(self.recompute_editor_sizes, content)
        content.installEventFilter(watcher)
        # keep a reference so python GC doesn't delete it
        scroll._resize_watcher = watcher'''