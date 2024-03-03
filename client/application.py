from client import Client
from download import DownloadManager
import dialogs

import os
import json
import webbrowser

from PySide6.QtWidgets import QMainWindow, QMessageBox, QDialog
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEvent
from PySide6.QtGui import QFontDatabase, QIcon


CUR_DIR = os.path.dirname(__file__)


class Application(QMainWindow):
    def __init__(self):
        super().__init__()

        self.loader = QUiLoader()
        self.download_manager = DownloadManager(folder_path="images")

        self.client = Client()

        self._init_interface()
        self._init_connexions()

        self.client.start()
        self.window.show()  # Shows the UI

    def _init_interface(self):
        """Initializes the user interface.

        This method loads the UI layout from a file, sets up the central widget, and initializes UI components like the completer and icon sizes.
        """
        self.window = self.loader.load(os.path.join(CUR_DIR, "design", "application.ui"), self)  # Loads UI file
        self.window.setWindowIcon(QIcon(os.path.join(CUR_DIR, "resources", "icon.ico")))
        self.setCentralWidget(self.window)

        self.regular_font_family = QFontDatabase.applicationFontFamilies(
            QFontDatabase.addApplicationFont(os.path.join(CUR_DIR, "fonts", "SpaceMono-Regular.ttf"))
        )[0]
        self.bold_font_family = QFontDatabase.applicationFontFamilies(
            QFontDatabase.addApplicationFont(os.path.join(CUR_DIR, "fonts", "SpaceMono-Bold.ttf"))
        )[0]

        self.bold_css = f"""font-family:"{self.bold_font_family}";font-weight:bold;"""
        self.regular_css = f"""font-family:"{self.regular_font_family}";"""

        self.window.join_button.setFont(self.bold_font_family)
        self.window.send_button.setFont(self.bold_font_family)

        self.window.username_input.setFont(self.regular_font_family)
        self.window.chat_room_input.setFont(self.regular_font_family)
        self.window.message_input.setFont(self.regular_font_family)

        self.window.send_button.clicked.connect(self.send_message)

    def _init_connexions(self):
        """Sets up connections (event filters and signal-slot connections) for the UI components.

        This method installs an event filter for the main window and connects UI components like text inputs and buttons to their respective slot functions.
        """
        self.window.installEventFilter(self)  # Install the event filter

        self.window.message_input.returnPressed.connect(self.send_message)  # When enter key is pressed
        self.window.send_button.clicked.connect(self.send_message)
        self.window.join_button.clicked.connect(self.join_room)

        self.window.actionServerTokens.triggered.connect(self.open_server_tokens)
        self.window.actionGithub.triggered.connect(self.open_github)
        self.window.actionDocumentation.triggered.connect(self.open_documentation)

        self.client.received_message.connect(self.display_message)

    def open_server_tokens(self):
        dialog = dialogs.ServerTokens(self)
        if dialog.window.exec() == QDialog.Accepted:
            ip, port = dialog.window.le_ip.text(), dialog.window.le_port.text()
            self.client.restart(ip, port)
        print(f"{self.client.address=}")

    def open_documentation(self):
        dialogs.Documentation(self).window.exec()

    def open_github(self):
        webbrowser.open("https://github.com/Umyedi/chat-app")

    def join_room(self):
        self.user_id = self.window.username_input.text()
        self.room_id = self.window.chat_room_input.text()
        join_message = json.dumps(
            {
                "action": "join",
                "user": {"username": f"{self.user_id}"},
                "room_id": self.room_id,
            }
        )
        self.client.socket.send(join_message.encode("utf-8"))

    def send_message(self):
        content = self.window.message_input.text()
        message = json.dumps(
            {
                "action": "message",
                "room_id": self.room_id,
                # "content": html.escape(content),
                "content": content,
            }
        )
        self.client.socket.send(message.encode("utf-8"))
        self.window.message_input.clear()

    def display_message(self, message: bytes):
        message_data = json.loads(message)
        author = message_data["author"]["username"]
        content = message_data["content"]
        color = message_data["author"]["color"]

        if content.startswith("https://oaidalleapiprodscus.blob.core.windows.net/"):  # url for openai image downloads
            image_path = self.download_manager.download_image(image_url=content, suffix="png")
            html_content = f'<img src="{image_path}"><br>'
        else:
            html_content = f"""<span style='{self.bold_css}color:{color};'>{author}: </span><span style='{self.regular_css}'>{content}</span><br>"""

        self.window.chat_view.insertHtml(html_content)
        self.window.chat_view.verticalScrollBar().setValue(self.window.chat_view.verticalScrollBar().maximum())

    def eventFilter(self, source, event):
        if event.type() != QEvent.Close or source is not self.window:
            return super().eventFilter(source, event)  # Call the base class method for other events

        if not self.client.is_running:
            event.accept()
            QApplication.quit()  # Quit the application

        reply = QMessageBox.question(
            self.window,
            "Warning",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.client.stop()  # Stop the server listener thread
            event.accept()
            QApplication.quit()  # Quit the application
        else:
            event.ignore()
        return True  # Indicates that the event is handled
