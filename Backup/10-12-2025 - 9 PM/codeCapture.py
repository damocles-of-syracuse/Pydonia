# codeCapture.py
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
import code
import time
from PyQt6.QtCore import QThread, pyqtSignal


class CodeCapture(QThread):
    output = pyqtSignal(str)
    # finished = pyqtSignal()

    def __init__(self, console: code.InteractiveConsole, cell_code: str, worker_queue: list, busy_flag: list, wid: int):
        super().__init__()
        self.cell_code = cell_code
        self.console = console
        self.worker_queue = worker_queue
        self.wid = wid
        self.busy_flag = busy_flag
        # self.outputLabel = outputLabel

    def run(self):
        if (not (len(self.worker_queue) == 0)) or self.busy_flag[0]:
            self.worker_queue.append(self.wid)

            self.output.emit(". . .")

            while self.wid in self.worker_queue:
                time.sleep(.01)

        self.busy_flag[0] = True
        self.output.emit(". . .")
        time.sleep(.015)


        try:
            code_obj = compile(self.cell_code, "<string>", "exec")
        except Exception:
            tb = traceback.format_exc()
            self.output.emit(tb)
            return  # stop: can't runcode without code_obj

        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                self.console.runcode(code_obj)
            except Exception:
                # runcode may call showtraceback already, but ensure we capture any other
                buf.write("\n" + traceback.format_exc())

        self.output.emit(buf.getvalue())

