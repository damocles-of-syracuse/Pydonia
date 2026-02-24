from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtGui import QTextCharFormat, QTextFormat, QPainter, QTextObjectInterface, QTextCursor
from PyQt5.QtCore import QSizeF, Qt, QRectF, QObject

FRACTION_OBJECT_TYPE = QTextFormat.UserObject + 1

class FractionObject(QObject, QTextObjectInterface):
    def __init__(self, parent=None):
        super().__init__(parent)

    def intrinsicSize(self, doc, posInDocument, format):
        return QSizeF(40, 30)

    def drawObject(self, painter, rect, doc, posInDocument, format):
        painter.save()
        numerator = format.property(1) or "?"
        denominator = format.property(2) or "?"
        painter.drawText(QRectF(rect.x(), rect.y(), rect.width(), rect.height()/2),
                         Qt.AlignCenter, numerator)
        line_y = rect.y() + rect.height()/2
        painter.drawLine(int(rect.x()), int(line_y), int(rect.x()) + int(rect.width()), int(line_y))
        painter.drawText(QRectF(rect.x(), line_y, rect.width(), rect.height()/2),
                         Qt.AlignCenter, denominator)
        painter.restore()

app = QApplication([])

editor = QTextEdit()

fraction_obj = FractionObject()
editor.document().documentLayout().registerHandler(FRACTION_OBJECT_TYPE, fraction_obj)

cursor = editor.textCursor()
cursor.insertText("Here is a fraction: ")

char_format = QTextCharFormat()
char_format.setObjectType(FRACTION_OBJECT_TYPE)
char_format.setProperty(1, "x+1")
char_format.setProperty(2, "y")

cursor.insertText(chr(0xfffc), char_format)
cursor.insertText(" and more text.")

editor.show()
app.exec_()
