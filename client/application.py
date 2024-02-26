"""

Ce fichier gère l'interface du projet avec le module PySide6.

TODO:
    - (FIX) Add a thread when the image is downloading
    - Add a command /ask [prompt] to ask something to a bot
    - Implement the mini games
    - Make a doc (+ class schema)
    - Clean the code
    - Create an installer
"""

import sys
import html
import requests
from client import Client
from worker import Worker
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem, QLabel, QCompleter
from PySide6.QtCore import Qt, QEvent, QSize, QStringListModel, QThread
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QColor, QFontMetrics, QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.thread = QThread()  # Manage the worker to do multithreading
        self.loader = QUiLoader()  # Allows to import .ui files
        self.client = Client("localhost", 5555)  # Creates a client to talk with the server

        self.user_id = None
        self.session_id = None
        self.username = None
        self.chat_history = {}
        self.color_table = {}

        self.commands = [
            "/help",
            "/time",
            "/image [prompt]",
            "/games",
            "/invite [game] [player]",
            "/accept [player]",
            "/play [action]",
        ]

        self.init_interface()
        self.init_connexions()

        self.window.show()  # Shows the UI

    def start_thread(self):
        """Starts the worker thread and initializes the worker.

        This method creates a new worker instance, moves it to a separate thread, and connects signals and slots for communication. The thread is then started.
        """
        self.worker = Worker(self.client, self.session_id, self.user_id)
        self.worker.moveToThread(self.thread)
        self.worker.update_users_signal.connect(self.refresh_users_list)
        self.worker.update_chat_signal.connect(self.update_messages)

        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.worker.deleteLater)

        self.thread.start()

    def stop_thread(self):
        """Stops the worker thread.

        This method signals the worker to stop, then quits the thread and waits for it to finish.
        """
        if self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()

    def init_interface(self):
        """Initializes the user interface.

        This method loads the UI layout from a file, sets up the central widget, and initializes UI components like the completer and icon sizes.
        """
        self.window = self.loader.load("../design/application.ui", self)  # Loads UI file
        self.setCentralWidget(self.window)

        self.completer = QCompleter()

        self.window.lw_chat_history.setIconSize(QSize(500, 500))

    def init_connexions(self):
        """Sets up connections (event filters and signal-slot connections) for the UI components.

        This method installs an event filter for the main window and connects UI components like text inputs and buttons to their respective slot functions.
        """
        self.window.installEventFilter(self)  # Install the event filter

        self.window.le_chat_input.setCompleter(self.completer)
        self.window.le_chat_input.textChanged.connect(self.on_text_changed)
        self.window.le_chat_input.returnPressed.connect(self.send_chat)  # When enter key is pressed
        self.window.pb_game.clicked.connect(self.join_game)

    def button_style_join(self):
        self.window.pb_game.setText("Leave")
        self.window.pb_game.setStyleSheet("background-color: #ff0021")
        self.window.le_username.setEnabled(False)
        self.window.le_room_id.setEnabled(False)

        self.window.pb_game.clicked.disconnect()
        self.window.pb_game.clicked.connect(self.leave_game)

    def button_style_leave(self):
        self.window.pb_game.setText("Join")
        self.window.pb_game.setStyleSheet("background-color: #5cdb5c")
        self.window.le_username.setEnabled(True)
        self.window.le_room_id.setEnabled(True)

        self.window.pb_game.clicked.disconnect()
        self.window.pb_game.clicked.connect(self.join_game)

    def attempt_join_game(self):
        response = self.client.join_game(self.session_id, self.username)
        if response["status"] == "success":
            self.user_id = response["data"]["user-id"]
            self.window.le_username.setText(f"{self.username}#{self.user_id}")
            self.start_thread()
        else:
            QMessageBox.critical(self, response["status"], response["message"])

    def join_game(self):
        self.session_id = self.window.le_room_id.text()
        self.username = self.window.le_username.text()

        self.window.lw_chat_history.clear()

        if "#" in self.username:  # Login with username and id
            self.username, self.user_id = self.username.split("#")
            self.start_thread()
        else:
            self.attempt_join_game()

        self.button_style_join()

    def leave_game(self):
        self.chat_history = {}
        self.window.lw_chat_history.clear()
        self.window.lw_users.clear()
        self.stop_thread()
        self.button_style_leave()

    def format_user_message(self, username: str, message: str) -> QLabel:
        color_hex = self.color_table.get(username, "A1A1A1")  # Default color is gray if username is not found

        item, label = QListWidgetItem(), QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)

        if username == "system" and message.startswith("https://"):
            self.add_image_from_url(message)
            return (None, None)
        elif username == "system":
            label.setText(f"<b>{username}:</b> <i>{message}</i>")
        else:
            message = html.escape(message)  # Prevent the user from using html
            label.setText(f"<b><span style='color:#{color_hex}'>{username}:</span></b> {message}")

        # Estimates the required height for the item
        width = label.width()
        fontMetrics = QFontMetrics(label.font())
        rect = fontMetrics.boundingRect(0, 0, width, 0, Qt.TextFlag.TextWordWrap, message)
        estimatedHeight = rect.height() + 20
        item.setSizeHint(QSize(width, estimatedHeight))

        return (item, label)

    def add_image_from_url(self, message):
        response = requests.get(message)
        image_data = response.content

        pixmap = QPixmap()
        pixmap.loadFromData(image_data)

        list_item = QListWidgetItem()
        list_item.setIcon(pixmap)

        self.window.lw_chat_history.addItem(list_item)

    def update_messages(self, chat_history):

        new_messages = {  # Adds the new messages to the dict
            timestamp: chat_history[timestamp]
            for timestamp in chat_history.keys()
            if timestamp not in self.chat_history
        }

        for timestamp in new_messages:
            username = new_messages[timestamp]["username"]
            content = new_messages[timestamp]["content"]
            self.chat_history[timestamp] = new_messages[timestamp]

            item, label = self.format_user_message(username, content)
            if item and label:
                self.window.lw_chat_history.addItem(item)
                self.window.lw_chat_history.setItemWidget(item, label)

        if new_messages:
            self.window.lw_chat_history.scrollToBottom()

    def refresh_users_list(self, users):
        self.window.lw_users.clear()
        for user in users:
            username, color = user["username"], user["color"]
            self.color_table[username] = color
            item = QListWidgetItem(username)
            item.setForeground(QColor(f"#{color}"))
            self.window.lw_users.addItem(item)

    def send_chat(self):
        message = self.window.le_chat_input.text()
        if message:
            self.client.send_chat(self.user_id, self.session_id, message)
            self.window.le_chat_input.clear()

    def on_text_changed(self, message):
        if message.startswith("/"):
            filtered_commands = [cmd for cmd in self.commands if cmd.startswith(message)]
            self.completer.setModel(QStringListModel(filtered_commands))
        else:
            self.completer.setModel(QStringListModel([]))

    def eventFilter(self, source, event):
        if event.type() != QEvent.Close or source is not self.window:
            return super().eventFilter(source, event)  # Call the base class method for other events

        if not self.thread.isRunning():
            self.stop_thread()
            self.quit(event)

        reply = QMessageBox.question(
            self,
            "Warning",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.stop_thread()
            self.quit(event)
        else:
            event.ignore()
        return True  # Indicate that the event was handled

    def quit(self, event):
        self.stop_thread()
        event.accept()
        QApplication.quit()  # Quit the application


def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication()
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
