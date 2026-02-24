import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter
from PyQt6.uic import loadUi
import sys
import os

from terminalWidget import TerminalWidget

class Window(QMainWindow):
    def __init__(self):
        self.terminalNum = 0
        super(Window, self).__init__()
        loadUi("./pydoniaMainWindow.ui", self)

        # Create the horizontal splitter
        self.HorizontalSplitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        # Add widgets to the splitter
        self.HorizontalSplitter.addWidget(self.ToolsFrame)
        self.HorizontalSplitter.addWidget(self.FileViewer)
        # Add the splitter to the MainFrame's layout
        self.MainFrameLayout.addWidget(self.HorizontalSplitter)
        # Set initial sizes
        self.HorizontalSplitter.setSizes([200, 600])

        # Create the Tools Vertical Splitter
        self.ToolsSplitter = QSplitter(QtCore.Qt.Orientation.Vertical)
        # Add widgets to the splitter
        self.ToolsSplitter.addWidget(self.FileMap)
        self.ToolsSplitter.addWidget(self.SymbolMenu)
        # Add the splitter to the MainFrame's layout
        self.ToolsFrameLayout.addWidget(self.ToolsSplitter)

        self.loadFileMap()

        tabs = self.FileViewer
        tabs.tabCloseRequested.connect(lambda index: self.on_tab_close(tabs, index))

        self.actionTerminal.triggered.connect(self.new_terminal_tab)

    def loadFileMap(self):
        # Get the current working directory
        current_project_dir = os.getcwd()
        # Create the file system model
        self.fileMapModel = QtGui.QFileSystemModel()
        # Set the model for the tree view
        self.FileMap.setModel(self.fileMapModel)
        self.fileMapModel.setIconProvider(QtWidgets.QFileIconProvider())
        # Set the root path of the model to the current working directory
        self.fileMapModel.setRootPath(current_project_dir)
        # Set the root index of the view to the current directory
        root_index = self.fileMapModel.index(current_project_dir)
        self.FileMap.setRootIndex(root_index)

        #print("Root Path:", model.rootPath())
        #print("Root Index:", root_index.data())

        # self.FileMap.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.FileMap.customContextMenuRequested.connect(self.FileMap_context_menu)

        self.FileMap.doubleClicked.connect(lambda: self.open_file(False))

        self.actionSave.triggered.connect(self.save_file)

    def FileMap_context_menu(self):
        menu = QtWidgets.QMenu()

        open = menu.addAction("Open")
        open.triggered.connect(lambda: self.open_file(False))

        open_as_txt = menu.addAction("Open As Text")
        open_as_txt.triggered.connect(lambda: self.open_file(True))

        new = menu.addMenu("New")
        newPy = new.addAction("Python File")
        newPy.triggered.connect(lambda: self.new_file(True))
        newText = new.addAction("Text File")
        newText.triggered.connect(lambda: self.new_file(False))
        newDir = new.addAction("Folder")
        newDir.triggered.connect(self.new_dir)

        cursor = QtGui.QCursor()
        menu.exec(cursor.pos())

    def new_dir(self):
        index = self.FileMap.currentIndex()
        path = self.fileMapModel.filePath(index)

        if os.path.isfile(path):
            path = os.path.dirname(path)

        # Ask user for name
        name, ok = QtWidgets.QInputDialog.getText(QtWidgets.QWidget(), "New Directory", "Enter folder name:")

        if ok and name:
            new_path = os.path.join(path, name)
            try:
                os.makedirs(new_path)
                return new_path
            except FileExistsError:
                self.statusBar().showMessage(f"Folder already exists", 3000)
            except OSError:
                self.statusBar().showMessage(f"Invalid folder name or permissions", 3000)
            except Exception as e:
                print(e)
                self.statusBar().showMessage(f"Something went worng {e}", 3000)
        else:
            self.statusBar().showMessage(f"Canceled folder creation", 3000)

        return False

    def new_file(self, pyth):
        index = self.FileMap.currentIndex()
        path = self.fileMapModel.filePath(index)

        if os.path.isfile(path):
            path = os.path.dirname(path)

        # Ask user for filename
        filename, ok = QtWidgets.QInputDialog.getText(QtWidgets.QWidget(), "New File", "Enter filename:")

        if ok and filename:
            if pyth:
                filename = f"{filename}.py"
            else:
                filename = f"{filename}.txt"

            new_path = os.path.join(path, filename)

            try:
                with open(new_path, "x") as f:
                    f.write("")  # Create empty file
                return new_path

            except FileExistsError:
                self.statusBar().showMessage("File already exists", 3000)

            except OSError:
                self.statusBar().showMessage("Invalid file name or permissions", 3000)

            except Exception as e:
                print(e)
                self.statusBar().showMessage(f"Something went wrong: {e}", 3000)

        else:
            self.statusBar().showMessage("Canceled file creation", 3000)

        return False

    def open_file(self, as_txt):
        file_index = self.FileMap.currentIndex()
        file_path = self.fileMapModel.filePath(file_index)
        # print(file_path)
        # os.startfile(file_path)
        if not (os.path.isfile(file_path) and (file_path.endswith('.txt') or (file_path.endswith('.py') and as_txt))):
            if os.path.isfile(file_path):
                if file_path.endswith('.py'):
                    self.open_py_file()
                    return
                self.statusBar().showMessage("Selected item is not a .txt or .py file.", 3000)
            return

        file_name = os.path.basename(file_path)
        # tab_index = self.FileViewer.addTab(QtWidgets.QLabel(file_path), file_name)
        editor = QtWidgets.QTextEdit()
        editor.file_path = file_path
        editor.setTabStopDistance(4 * editor.fontMetrics().horizontalAdvance(" "))
        editor.document().setModified(False)

        # add editor to tab widget
        tab_index = self.FileViewer.addTab(editor, file_name)
        self.FileViewer.setCurrentIndex(tab_index)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                editor.setText(f.read())
                editor.document().modificationChanged.connect(self.update_txt_tab_title)
        except Exception as e:
            print(f"Failed to open file: {e}")
            self.statusBar().showMessage(f"Failed to open file: {e}", 3000)
            return

    def open_py_file(self):
        file_index = self.FileMap.currentIndex()
        file_path = self.fileMapModel.filePath(file_index)
        file_name = os.path.basename(file_path)

        # Create a scrollable container to hold multiple editors + labels
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.file_path = file_path
        scroll.setFont(QtGui.QFont("Times New Roman", 14))

        content = QtWidgets.QWidget()

        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            # print(f"Failed to open file: {e}")
            self.statusBar().showMessage(f"Failed to open file: {e}", 3000)
            return

        # Split into segments separated by lines that are exactly "#---"
        segments = []
        current_lines = []
        for line in lines:
            if line.strip() == "#---":
                # Remove trailing newline from the last line if it exists
                if current_lines and current_lines[-1].endswith('\n'):
                    current_lines[-1] = current_lines[-1][:-1]
                segments.append(''.join(current_lines))
                current_lines = []
            else:
                current_lines.append(line)

        # Append the last segment
        segments.append(''.join(current_lines))

        # Create a QTextEdit followed by a QLabel("Temp") for each segment
        for idx, seg_text in enumerate(segments):
            editor = QtWidgets.QTextEdit()
            editor.segment_index = idx  # Which segment this editor holds
            editor.setPlainText(seg_text)
            editor.setFont(QtGui.QFont("Times New Roman", 14))
            editor.document().setDefaultFont(QtGui.QFont("Times New Roman", 14))
            editor.setTabStopDistance(4 * editor.fontMetrics().horizontalAdvance(" "))
            editor.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
            editor.document().setModified(False)
            # connect modification signal so existing update_tab logic still works
            try:
                editor.document().modificationChanged.connect(self.update_py_tab_title)
                editor.document().documentLayout().documentSizeChanged.connect(self.recompute_editor_sizes)
                # editor.document().contentsChanged
            except Exception:
                print("editor connections failed")

            content_layout.addWidget(editor)

            output = QtWidgets.QLabel("")
            output.setFont(QtGui.QFont("Times New Roman", 14))
            output.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
            content_layout.addWidget(output)

        newCell = QtWidgets.QPushButton("Click to insert a new cell")
        newCell.setFont(QtGui.QFont("Times New Roman", 10))
        newCell.setFixedHeight(35)
        newCell.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        newCell.clicked.connect(self.insert_new_cell)

        content_layout.addWidget(newCell) # , alignment=QtCore.Qt.AlignmentFlag.AlignHCenter

        effect = QtWidgets.QGraphicsOpacityEffect(newCell)
        newCell.setGraphicsEffect(effect)
        effect.setOpacity(0.0)

        def _enter(e):
            effect.setOpacity(1.0)

        def _leave(e):
            effect.setOpacity(0.0)

        newCell.enterEvent = _enter
        newCell.leaveEvent = _leave


        # push content to top if there is extra space
        content_layout.addStretch()

        spacer_widget = QtWidgets.QWidget()
        spacer_widget.setFixedHeight(800)
        content_layout.addWidget(spacer_widget)

        scroll.setWidget(content)

        # add the scroll area as the tab content
        tab_index = self.FileViewer.addTab(scroll, file_name)
        self.FileViewer.setCurrentIndex(tab_index)

        self.recompute_editor_sizes()

    def new_terminal_tab(self):
        """
        Add a new tab to self.FileViewer with a TerminalWidget.
        """
        term = TerminalWidget()

        try:
            term.start_shell(cwd=None)
            self.terminalNum += 1
            tab_title = f"Terminal {self.terminalNum}"
        except Exception as e:
            self.statusBar().showMessage(f"Failed to start terminal: {e}", 3000)
            return

        # Add the terminal widget to a new tab
        index = self.FileViewer.addTab(term, tab_title)
        self.FileViewer.setCurrentIndex(index)

        # Make sure the process is terminated when the tab/widget is closed.
        def on_widget_destroyed(_=None):
            try:
                term.terminate()
                self.terminalNum -= 1
            except Exception:
                pass

        term.destroyed.connect(on_widget_destroyed)
        term.input.setFocus()

    def recompute_editor_sizes(self):
        """Recompute each editor's height to fit contents."""
        scroll = self.FileViewer.currentWidget()
        if not scroll:
            return

        widget = scroll.widget()
        editors = widget.findChildren(QtWidgets.QTextEdit)

        for ed in editors:
            ed.viewport().update()  # ensure viewport geometry is current
            doc = ed.document()

            # document().size().height() returns the laid-out height in pixels; add frame & margins
            doc_height = int(doc.size().height())
            doc_margin = int(doc.documentMargin())

            new_height = max(20, doc_height + doc_margin)
            ed.setFixedHeight(new_height)

    def insert_new_cell(self):
        scroll = self.FileViewer.currentWidget()
        if not scroll:
            self.statusBar().showMessage(f"Failed to insert cell", 3000)
            return

        widget = scroll.widget()
        content_layout = widget.layout()
        idx = len(widget.findChildren(QtWidgets.QTextEdit))

        editor = QtWidgets.QTextEdit()
        editor.segment_index = idx  # Which segment this editor holds
        editor.setPlainText("")
        editor.setFont(QtGui.QFont("Times New Roman", 14))
        editor.document().setDefaultFont(QtGui.QFont("Times New Roman", 14))
        editor.setTabStopDistance(4*editor.fontMetrics().horizontalAdvance(" "))
        editor.document().setModified(True)
        # connect modification signal so existing update_tab logic still works
        try:
            editor.document().modificationChanged.connect(self.update_py_tab_title)
            editor.document().documentLayout().documentSizeChanged.connect(self.recompute_editor_sizes)
            # editor.document().contentsChanged
        except Exception:
            print("editor connections failed")

        content_layout.insertWidget(content_layout.count() - 3, editor)

        output = QtWidgets.QLabel("")
        output.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        content_layout.insertWidget(content_layout.count() - 3, output)

        self.update_py_tab_title()

        # force immediate layout pass
        widget.adjustSize()
        widget.updateGeometry()
        content_layout.update()
        QtWidgets.QApplication.processEvents()  # synchronous — lets Qt finish layout changes

        # QtCore.QTimer.singleShot(0, self.recompute_editor_sizes)

        self.recompute_editor_sizes()

        # scrollbar = scroll.verticalScrollBar()
        # QtCore.QTimer.singleShot(0, lambda: scrollbar.setValue(scrollbar.maximum()))

    def save_file(self, tabs=None, index=None):
        """ Save the tab. If tabs and index are provided, save that tab, otherwise save current tab. """
        # Use explicit None check so index == 0 is handled correctly
        if tabs is not None and index is not None:
            widget = tabs.widget(index)
        else:
            widget = self.FileViewer.currentWidget()

        if widget is None:
            self.statusBar().showMessage("Nothing to save", 3000)
            return False

        path = getattr(widget, "file_path", None)
        if not path:
            self.statusBar().showMessage("Nothing to save", 3000)
            return False

        # Plain text editor case
        if isinstance(widget, QtWidgets.QTextEdit):
            saved = self._save_to_path(widget.toPlainText(), path)
            if saved:
                widget.document().setModified(False)
            return saved

        # Scroll area (py file with segments) — write entire content in one go
        elif isinstance(widget, QtWidgets.QScrollArea):
            editors = widget.findChildren(QtWidgets.QTextEdit)
            # join with separator exactly like your loader expects
            full_text = "\n#---\n".join(ed.toPlainText() for ed in editors)
            saved = self._save_to_path(full_text, path)
            if saved:
                for ed in editors:
                    ed.document().setModified(False)
            return saved

        else:
            self.statusBar().showMessage("Nothing to save", 3000)
            return False

    def _append_to_path(self, text, path):
        """append the text to the bottom of path"""
        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Save Error", f"Could not save file:\n{e}")
            return False
        # mark document as saved
        return True

    def _save_to_path(self, text, path):
        """Write the text to path"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Save Error", f"Could not save file:\n{e}")
            return False
        # mark document as saved
        return True

    def update_py_tab_title(self, modified=None):
        """Set tab title for a scroll-area-backed python file when any segment changes."""
        sender_doc = self.sender()
        target_scroll = None
        target_index = None

        # find the scroll area that contains the editor whose document is sender_doc
        for i in range(self.FileViewer.count()):
            w = self.FileViewer.widget(i)
            if isinstance(w, QtWidgets.QScrollArea):
                container = w.widget()
                for ed in container.findChildren(QtWidgets.QTextEdit):
                    if ed.document() is sender_doc:
                        target_scroll = w
                        target_index = i
                        break
                if target_scroll:
                    break

        # fallback to focused scroll area
        if target_scroll is None:
            widget = self.FileViewer.currentWidget()
            if not isinstance(widget, QtWidgets.QScrollArea):
                return
            target_scroll = widget
            target_index = self.FileViewer.currentIndex()

        # determine modified status across all editors in this scroll
        container = target_scroll.widget()
        mod = any(ed.document().isModified() for ed in container.findChildren(QtWidgets.QTextEdit))
        file_name = os.path.basename(target_scroll.file_path)
        star = "*" if mod else ""
        self.FileViewer.setTabText(target_index, f"{star}{file_name}")

    def update_txt_tab_title(self, modified=None):
        """Update tab title for a plain text editor whose document changed."""
        sender_doc = self.sender()  # QPlainTextDocument or QTextDocument
        target_index = None
        target_editor = None

        # find editor whose document() is sender_doc
        for i in range(self.FileViewer.count()):
            w = self.FileViewer.widget(i)
            if isinstance(w, QtWidgets.QTextEdit) and w.document() is sender_doc:
                target_index = i
                target_editor = w
                break

        # fallback: use current widget if we didn't find it
        if target_editor is None:
            target_index = self.FileViewer.currentIndex()
            target_editor = self.FileViewer.currentWidget()
            if not isinstance(target_editor, QtWidgets.QTextEdit):
                return

        file_name = os.path.basename(target_editor.file_path)
        star = "*" if target_editor.document().isModified() else ""
        self.FileViewer.setTabText(target_index, f"{star}{file_name}")

    def on_tab_close(self, tabs, index):
        widget = tabs.widget(index)
        if widget is None:
            return

        try:
            title = tabs.tabText(index) or ""
            if title.startswith('*'):
                # Ask the user
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle("Confirmation")
                msg_box.setText("Tab has unsaved changes. Do you want to save before closing?")
                msg_box.setStandardButtons(
                    QtWidgets.QMessageBox.StandardButton.Yes |
                    QtWidgets.QMessageBox.StandardButton.No |
                    QtWidgets.QMessageBox.StandardButton.Cancel
                )
                response = msg_box.exec()

                if response == QtWidgets.QMessageBox.StandardButton.Yes:
                    saved = self.save_file(tabs, index)
                    QApplication.processEvents()
                    if saved:
                        tabs.removeTab(index)
                        widget.deleteLater()
                    else:
                        # save failed; do not close
                        return
                elif response == QtWidgets.QMessageBox.StandardButton.No:
                    tabs.removeTab(index)
                    widget.deleteLater()
                else:
                    # Cancel -> do nothing
                    return
            else:
                tabs.removeTab(index)
                widget.deleteLater()
        except Exception as e:
            self.statusBar().showMessage(f"Issue with tab deletion: {e}", 3000)

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        Called when the window is closing. Iterate through tabs and, for any
        whose tab text begins with '*', ask the user whether to save.
        """

        for i in range(self.FileViewer.count() - 1, -1, -1):
            title = self.FileViewer.tabText(i)
            if title and title.startswith('*'):
                # ask the user
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle("Confirmation")
                msg_box.setText(f"Tab '{title.lstrip('*')}' has unsaved changes. Save before leaving?")
                msg_box.setStandardButtons(
                    QtWidgets.QMessageBox.StandardButton.Yes |
                    QtWidgets.QMessageBox.StandardButton.No |
                    QtWidgets.QMessageBox.StandardButton.Cancel
                )
                response = msg_box.exec()

                if response == QtWidgets.QMessageBox.StandardButton.Yes:
                    try:
                        ok = self.save_file(self.FileViewer, i)
                    except Exception as e:
                        # Save failed — show message and abort closing
                        QtWidgets.QMessageBox.critical(self, "Save failed", f"could not save '{title}':\n{e}")
                        event.ignore()
                        return
                    if not ok:
                        # save_file indicated failure — abort closing
                        event.ignore()
                        return

                elif response == QtWidgets.QMessageBox.StandardButton.No:
                    pass
                else:  # Cancel
                    # abort closing the window
                    event.ignore()
                    return

        # If we get here, user didn't cancel — accept the close
        event.accept()
        super().closeEvent(event)




def main():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()