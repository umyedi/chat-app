import sys
from application import Application
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)  # Avoids OpenGL error message
    app = QApplication()
    window = Application()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()