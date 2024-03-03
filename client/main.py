from application import Application

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)  # Avoid OpenGL error message
    app = QApplication()
    window = Application()
    sys.exit(app.exec())
