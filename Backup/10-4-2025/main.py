import PyQt6
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QSizePolicy, QApplication, QMainWindow, QSplitter
from PyQt6.uic import loadUi
import sys
import os

from sympy import Lambda


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

        self.FileMap.doubleClicked.connect(self.open_file)

        self.actionSave.triggered.connect(self.save_file)

    def FileMap_context_menu(self):
        menu = QtWidgets.QMenu()
        open = menu.addAction("Open")
        open.triggered.connect(self.open_file)
        cursor = QtGui.QCursor()
        menu.exec(cursor.pos())

    def open_file(self):
        file_index = self.FileMap.currentIndex()
        file_path = self.fileMapModel.filePath(file_index)
        # print(file_path)
        # os.startfile(file_path)
        if not (os.path.isfile(file_path) and file_path.endswith(('.txt', '.py'))):
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
                editor.document().modificationChanged.connect(self._update_tab_title)
        except Exception as e:
            print(f"Failed to open file: {e}")
            self.statusBar().showMessage(f"Failed to open file: {e}", 3000)
            return

    def save_file(self):
        """ Save the current tab. If the tab has no stored filepath, fall back to Save As. """
        editor = self.FileViewer.currentWidget()
        if editor is None:
            return

        path = getattr(editor, "file_path", None)
        if path:
            return self._save_to_path(editor, path)
        else:
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

    def _update_tab_title(self):
        """Set main window title to show current file and '*' when modified."""
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