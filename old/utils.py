# utils.py
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr
import code

def run_code_capture(console: code.InteractiveConsole, source: str) -> str:
    """Run source in `console` and return combined stdout+stderr (including syntax errors)."""
    # Try to compile first — catch SyntaxError / IndentationError, etc.
    try:
        codeobj = compile(source, "<string>", "exec")
    except Exception:
        # Return a full traceback string for compile-time errors
        return traceback.format_exc()

    buf = io.StringIO()
    # console.runcode will call showtraceback which writes to stderr;
    # by redirecting stderr we capture it.
    with redirect_stdout(buf), redirect_stderr(buf):
        console.runcode(codeobj)

    return buf.getvalue()

