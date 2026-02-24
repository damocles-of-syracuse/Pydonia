import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter
from PyQt6.uic import loadUi
import sys
import os

class Window(QMainWindow):
    def __init__(self):
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
        tabs.tabCloseRequested.connect(lambda index: tabs.removeTab(index))

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
        open.triggered.connect(lambda opn: self.open_file(False))
        open_as_txt = menu.addAction("Open As Text")
        open_as_txt.triggered.connect(lambda opn: self.open_file(True))
        cursor = QtGui.QCursor()
        menu.exec(cursor.pos())

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
        scroll.setFont(QtGui.QFont("Times New Roman", 16))

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
            # check for a line that is exactly "#---" (ignoring newline and surrounding whitespace)
            if line.strip() == "#---":
                segments.append(''.join(current_lines))
                current_lines = []
            else:
                current_lines.append(line)
        # append last segment (could be empty if the file ended with a comment)
        segments.append(''.join(current_lines))

        # Create a QTextEdit followed by a QLabel("Temp") for each segment
        for idx, seg_text in enumerate(segments):
            editor = QtWidgets.QTextEdit()
            editor.segment_index = idx  # Which segment this editor holds
            editor.setPlainText(seg_text)
            editor.setFont(QtGui.QFont("Times New Roman", 16))
            editor.document().setDefaultFont(QtGui.QFont("Times New Roman", 16))
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
            output.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
            content_layout.addWidget(output)

        newBox = QtWidgets.QPushButton("Click to insert a new box")
        newBox.setFont(QtGui.QFont("Times New Roman", 10))
        newBox.setFixedHeight(35)
        newBox.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        newBox.clicked.connect(self.insert_new_box)

        content_layout.addWidget(newBox) # , alignment=QtCore.Qt.AlignmentFlag.AlignHCenter

        effect = QtWidgets.QGraphicsOpacityEffect(newBox)
        newBox.setGraphicsEffect(effect)
        effect.setOpacity(0.0)

        def _enter(e):
            effect.setOpacity(1.0)

        def _leave(e):
            effect.setOpacity(0.0)

        newBox.enterEvent = _enter
        newBox.leaveEvent = _leave


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

    def insert_new_box(self):
        scroll = self.FileViewer.currentWidget()
        if not scroll:
            self.statusBar().showMessage(f"Failed to insert box", 3000)
            return

        widget = scroll.widget()
        content_layout = widget.layout()
        idx = len(widget.findChildren(QtWidgets.QTextEdit))

        editor = QtWidgets.QTextEdit()
        editor.segment_index = idx  # Which segment this editor holds
        editor.setPlainText("")
        editor.setFont(QtGui.QFont("Times New Roman", 16))
        editor.document().setDefaultFont(QtGui.QFont("Times New Roman", 16))
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

    def save_file(self):
        """ Save the current tab. If the tab has no stored filepath, fall back to Save As. """
        editor = self.FileViewer.currentWidget()
        if editor is None:
            self.statusBar().showMessage(f"Nothing to save", 3000)
            return

        path = getattr(editor, "file_path", None)
        if path:
            return self._save_to_path(editor, path)
        else:
            self.statusBar().showMessage(f"Nothing to save", 3000)
            return

    def _save_to_path(self, editor, path):
        """Write the editor contents to path, handle errors, clear modified flag."""
        try:
            text = editor.toPlainText()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Save Error", f"Could not save file:\n{e}")
            return False
        # mark document as saved
        editor.document().setModified(False)
        return True

    def update_py_tab_title(self):
        """Set tab title to show current file and '*' when modified."""
        scroll = self.FileViewer.currentWidget()
        if not scroll:
            return

        mod = False
        widget = scroll.widget()
        if widget:
            for ed in widget.findChildren(QtWidgets.QTextEdit):
                if ed.document().isModified():
                    mod = True
                    break

        file_name = os.path.basename(scroll.file_path)
        star = "*" if mod else ""
        self.FileViewer.setTabText(self.FileViewer.currentIndex(), f"{star}{file_name}")

    def update_txt_tab_title(self):
        """Set tab title to show current file and '*' when modified."""
        editor = self.FileViewer.currentWidget()
        if not editor:
            return
        file_name = os.path.basename(editor.file_path)
        star = "*" if editor.document().isModified() else ""
        self.FileViewer.setTabText(self.FileViewer.currentIndex(), f"{star}{file_name}")




def main():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()