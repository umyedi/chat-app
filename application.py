"""

Ce fichier gère l'interface du projet avec le module PySide6.

"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QThreadPool
from PySide6.QtUiTools import QUiLoader
from multithreading import Worker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()  # Manage multithreading
        self.loader = QUiLoader()  # Allows to import .ui files

        self.window = self.loader.load("design/application.ui", None)
        self.window.chat_input.returnPressed.connect(self.send_chat)
        self.window.show()

    def send_chat(self):
        message = self.window.chat_input.text()

        if not message:
            return

        self.window.chat_history.addItem(message)
        self.window.chat_input.clear()


def main():
    app = QApplication()
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
