from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QProcess
import os, sys

class SubprocessConsole(QtWidgets.QWidget):
    """Small console widget that connects to a QProcess running python -i -u file.py"""
    def __init__(self, python_executable=None, parent=None):
        super().__init__(parent)
        self.python_executable = python_executable or sys.executable

        # Output area (read-only)
        self.output = QtWidgets.QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setWordWrapMode(QtGui.QTextOption.WrapMode.NoWrap)

        # Single-line input
        self.input = QtWidgets.QLineEdit()
        self.input.returnPressed.connect(self._on_return)

        # Layout
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.output)
        lay.addWidget(self.input)

        # QProcess
        self.proc = QProcess(self)
        self.proc.readyReadStandardOutput.connect(self._read_stdout)
        self.proc.readyReadStandardError.connect(self._read_stderr)
        self.proc.started.connect(lambda: self._append_text("[process started]\n"))
        self.proc.finished.connect(self._on_finished)

    def start_interpreter_with_file(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(file_path)
        args = ['-i', '-u', file_path]
        self.proc.start(self.python_executable, args)

    def write_to_process(self, text: str):
        if not text.endswith("\n"):
            text += "\n"
        if self.proc.state() == QProcess.ProcessState.Running:
            self.proc.write(text.encode('utf-8'))
            self.proc.waitForBytesWritten(100)

    def _read_stdout(self):
        ba = self.proc.readAllStandardOutput()
        s = bytes(ba).decode('utf-8', errors='replace')
        self._append_text(s)

    def _read_stderr(self):
        ba = self.proc.readAllStandardError()
        s = bytes(ba).decode('utf-8', errors='replace')
        self._append_text("[stderr] " + s)

    def _append_text(self, text: str):
        self.output.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.output.insertPlainText(text)
        self.output.moveCursor(QtGui.QTextCursor.MoveOperation.End)

    def _on_return(self):
        line = self.input.text()
        # echo locally
        self._append_text(">>> " + line + "\n")
        self.write_to_process(line)
        self.input.clear()

    def _on_finished(self, exitCode, exitStatus):
        self._append_text(f"\n[process finished: code={exitCode} status={exitStatus}]\n")
