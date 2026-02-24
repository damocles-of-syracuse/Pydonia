"""
Inline-editable math using QWebEngineView + MathJax.

- Click a variable (e.g. the "N" in the formula).
- An inline <input> appears on top of the typeset variable.
- Edit, press Enter or click away -> value updates and MathJax re-typesets.
- Use the "Print values" button to get the current variables back in Python.
"""

import sys
import json
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QWidget, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView


HTML_TEMPLATE = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Inline-edit Math (MathJax)</title>

  <style>
    body {{ font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; margin:12px; }}
    #math-container {{ display:inline-block; position:relative; }}
    /* the inline input we create dynamically will have this class */
    .inline-input {{
      position: absolute;
      z-index: 9999;
      padding: 0;
      margin: 0;
      border: 1px solid #888;
      font: inherit;
      box-sizing: border-box;
      text-align: center;
      background: rgba(255,255,255,0.95);
    }}
    .var-highlight {{
      cursor: text;
    }}
  </style>

  <!-- MathJax v3 from CDN -->
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body>
  <div>
    <div id="math-container"></div>
  </div>
  <script>
    // mathTemplate: a TeX string with placeholders like {N}, {k}, etc.
    const mathTemplate = {math_template_json};
    // initial vars as a JS object
    let vars = {vars_json};

    // Build TeX to include \class macros so MathJax will tag the variable text
    // For a placeholder {N} we inject \class{{varN}}{{value}} so the rendered DOM will carry an identifiable class.
    function buildTex() {{
      // Replace {name} with \class{{var-<name>}}{{value}}
      // We must escape values that could contain bracing characters.
      let s = mathTemplate;
      for (const name of Object.keys(vars)) {{
        const val = String(vars[name]).replace(/([\\\\{}])/g, '\\\\$1'); // escape backslash and braces
        const replacement = `\\\\class{{var-${{name}}}}{{${{val}}}}`;
        // Replace all occurrences of {name}
        s = s.split('{{' + name + '}}').join(replacement);
        s = s.split('{' + name + '}').join(replacement);
      }}
      return s;
    }}

    // Render function: puts TeX into the container and asks MathJax to typeset it.
    async function render() {{
      const tex = buildTex();
      const container = document.getElementById('math-container');

      // Put inline math delimiters so MathJax processes as inline math
      container.innerHTML = "\\\\(" + tex + "\\\\)";

      // typeset only that container
      await MathJax.typesetPromise([container]);

      // after typesetting, attach click handlers to elements that have our class pattern
      attachVarHandlers();
    }}

    // Find rendered nodes that correspond to variables and attach handlers
    function attachVarHandlers() {{
      // classes applied by \class are added to the outermost produced element that corresponds to the math piece.
      // We gave names like var-N, var-k, etc.
      for (const name of Object.keys(vars)) {{
        const cls = 'var-' + name;
        const els = document.querySelectorAll('.' + cls);
        els.forEach(el => {{
          // Make sure it's visually clickable
          el.classList.add('var-highlight');

          // remove previous listener to avoid duplicates
          el.onclick = (ev) => {{
            ev.stopPropagation();
            startInlineEdit(name, el);
          }};
        }});
      }}
    }}

    // Create an <input> positioned over element 'el' and let the user edit vars[name]
    function startInlineEdit(name, el) {{
      // If an input already exists, remove it
      removeExistingInput();

      const rect = el.getBoundingClientRect();
      const containerRect = document.getElementById('math-container').getBoundingClientRect();

      // Create input
      const input = document.createElement('input');
      input.type = 'text';
      input.value = vars[name];
      input.className = 'inline-input';
      document.body.appendChild(input);

      // Position absolute relative to the page so we can place it exactly over element
      // Slightly expand input size to feel comfortable
      const left = Math.round(rect.left + window.scrollX - 1);
      const top = Math.round(rect.top + window.scrollY - 1);
      input.style.left = left + 'px';
      input.style.top = top + 'px';
      input.style.width = Math.max(30, Math.round(rect.width + 6)) + 'px';
      input.style.height = Math.max(20, Math.round(rect.height + 2)) + 'px';
      input.style.fontSize = window.getComputedStyle(el).fontSize || 'inherit';
      input.style.lineHeight = window.getComputedStyle(el).lineHeight || 'normal';

      input.focus();
      input.select();

      // commit on Enter or blur, cancel on Escape
      function commit() {{
        vars[name] = input.value;
        removeExistingInput();
        render();
        // optionally notify the Python side by updating window._lastVarsChanged if Python polls it
        window._lastVarsChanged = JSON.stringify(vars);
      }}
      function cancel() {{
        removeExistingInput();
      }}

      input.addEventListener('keydown', (e) => {{
        if (e.key === 'Enter') {{
          commit();
          e.preventDefault();
        }} else if (e.key === 'Escape') {{
          cancel();
          e.preventDefault();
        }}
      }});

      input.addEventListener('blur', () => {{
        commit();
      }});

      // Make helper to remove the input later
      window._removeInlineInput = () => {{
        if (input && input.parentNode) input.parentNode.removeChild(input);
        window._removeInlineInput = null;
      }};
    }}

    function removeExistingInput() {{
      if (window._removeInlineInput) window._removeInlineInput();
    }}

    // Helper for Python: return the current vars as a JSON string.
    window.getVarsJson = function () {{
      return JSON.stringify(vars);
    }};

    // allow Python to set vars (call from python via runJavaScript)
    window.setVarsJson = function (jsonStr) {{
      try {{
        const o = JSON.parse(jsonStr);
        vars = o;
        render();
        return true;
      }} catch (err) {{
        return false;
      }}
    }};

    // initial render
    render();
  </script>
</body>
</html>
"""

# ---------- Python / PyQt side ----------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, math_template, variables):
        super().__init__()
        self.setWindowTitle("Inline-editable Math (MathJax)")

        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        v.setContentsMargins(6, 6, 6, 6)

        # Web view
        self.view = QWebEngineView()
        v.addWidget(self.view, stretch=1)

        # Buttons row
        h = QHBoxLayout()
        v.addLayout(h)
        btn_print = QPushButton("Print values")
        btn_print.clicked.connect(self.print_values)
        h.addWidget(btn_print)
        btn_set = QPushButton("Set vars to N=4,k=2")
        btn_set.clicked.connect(self.set_example_vars)
        h.addWidget(btn_set)
        h.addStretch()

        # Build HTML with safe JSON injection
        math_template_json = json.dumps(math_template)
        vars_json = json.dumps(variables)
        math_template_json = json.dumps(math_template)
        vars_json = json.dumps(variables)
        html = HTML_TEMPLATE.replace("{math_template_json}", math_template_json) \
            .replace("{vars_json}", vars_json)

        # Load HTML. Use a base URL so external resources like CDN are allowed (absolute URLs work anyway).
        self.view.setHtml(html, QUrl("https://example.local/"))

        self.resize(800, 300)

    def print_values(self):
        # ask the page for the vars JSON, and print it (or do whatever)
        self.view.page().runJavaScript("getVarsJson();", self._print_callback)

    def _print_callback(self, result):
        try:
            obj = json.loads(result)
        except Exception:
            obj = result
        print("Current variables:", obj)

    def set_example_vars(self):
        new_vars = {"N": 4, "k": 2}
        js = f"setVarsJson({json.dumps(json.dumps(new_vars))});"
        # note: setVarsJson expects a JSON string argument (we double-json above)
        self.view.page().runJavaScript(js)


if __name__ == "__main__":
    # Example TeX template: use placeholders {N} and {k}
    # We'll inject values into {N} and {k}. They become \class{{var-N}}{{value}} inside the TeX.
    math_template = r'X_{k} = \sum_{n=0}^{\{N}-1} x_n \cdot e^{\frac{-i 2\pi k n}{\{N}}}'
    # The template uses {N} and {k}; code replaces those placeholders with class-wrapped values for MathJax
    variables = {"N": 8, "k": 0}

    app = QtWidgets.QApplication(sys.argv)

    w = MainWindow(math_template, variables)
    w.show()
    sys.exit(app.exec_())
