"""

Ce fichier gère l'interface du projet avec le module PySide6.

"""

import sys
from time import sleep
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem, QLabel, QCompleter
from PySide6.QtCore import QThreadPool, Signal, Qt, QEvent, QSize, QStringListModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QFont, QBrush, QColor, QIcon
from multithreading import Worker
from client.client import Client

# TODO:
# Implémenter la commande '/generate image [prompt]' qui génère une image avec DALLE-E
# Ajouter une couleur aux pseudos des gens
# Implémentation des minijeux
# ? Flèche haut : commande précédente
# Implémenter une fonction dans 'server.py' qui supprimes du json les utilisateurs non-connectés


class MainWindow(QMainWindow):

    update_chat_signal = Signal(dict)  # Signal to carry chat message as dict (avoids QTimer/threads problems)

    def __init__(self):
        super().__init__()

        self.threadpool = QThreadPool()  # Manage multithreading
        self.loader = QUiLoader()  # Allows to import .ui files
        self.client = Client("localhost", "5555")  # Creates a client to talk with the server

        self.user_id = None
        self.session_id = None
        self.username = None
        self.chat_history = {}
        self.color_table = {}
        self.is_running = False

        self.commands = ["/help", "/time", "/games", "/invite [game] [player]", "/accept [player]", "/play [action]",]
        self.init_interface()
        self.init_connexions()

        self.window.show()  # Show the UI

    def init_interface(self):
        self.window = self.loader.load("design/application.ui", self)  # Loads UI file
        self.setCentralWidget(self.window)

        # Créer un QCompleter avec un modèle vide pour commencer
        self.completer = QCompleter()
        self.window.le_chat_input.setCompleter(self.completer)

        self.window.lw_chat_history.setIconSize(QSize(500, 500))

    def init_connexions(self):
        self.window.installEventFilter(self)  # Install the event filter

        self.update_chat_signal.connect(self.update_chat_ui)

        self.window.le_chat_input.textChanged.connect(self.on_text_changed)
        self.window.le_chat_input.returnPressed.connect(self.send_chat)  # When enter key is pressed
        self.window.pb_game.clicked.connect(self.join_game)

    def join_game(self):
        self.session_id = self.window.le_room_id.text()
        self.username = self.window.le_username.text()

        if "#" in self.username:  # Login with username and id
            temp = self.username.split("#")
            self.username = temp[0]
            self.user_id = temp[1]
            worker = Worker(self.update_ui)
            self.threadpool.start(worker)
        else:
            response = self.client.join_game(self.session_id, self.username)
            if response["status"] == "success":
                self.user_id = response["data"]["user-id"]
                self.window.le_username.setText(f"{self.username}#{self.user_id}")
                worker = Worker(self.update_ui)
                self.threadpool.start(worker)
            else:
                QMessageBox.critical(self, response["status"], response["message"])
                return

        # Change button and line edit styles
        self.window.pb_game.setText("Leave")
        self.window.pb_game.setStyleSheet("background-color: #ff0021")
        self.window.le_username.setEnabled(False)
        self.window.le_room_id.setEnabled(False)

        self.window.pb_game.clicked.disconnect()
        self.window.pb_game.clicked.connect(self.leave_game)

    def leave_game(self):
        self.is_running = False

        # Change button and line edit styles
        self.window.pb_game.setText("Join")
        self.window.pb_game.setStyleSheet("background-color: #5cdb5c")
        self.window.le_username.setEnabled(True)
        self.window.le_room_id.setEnabled(True)

        self.window.pb_game.clicked.disconnect()
        self.window.pb_game.clicked.connect(self.join_game)

    def update_ui(self):
        self.is_running = True
        while self.is_running:
            response = self.client.get_game_status(self.session_id, self.user_id)

            if response["status"] == "error":
                QMessageBox.critical(self, response["status"], response["message"])
                return

            chat_history = response["data"]["chat_history"]

            self.update_chat_signal.emit(chat_history)
            self.update_users_list_ui(response["data"]["users"])

            sleep(0.5)

    def update_chat_ui(self, chat_history):

        new_messages = {
            timestamp: chat_history[timestamp]
            for timestamp in chat_history.keys()
            if timestamp not in self.chat_history
        }

        for timestamp in new_messages:
            username = new_messages[timestamp]["username"]
            content = new_messages[timestamp]["content"]
            self.chat_history[timestamp] = new_messages[timestamp]

            item = self.format_message(username, content)

            self.window.lw_chat_history.addItem(item)
            self.window.lw_chat_history.scrollToBottom()

        # if new_messages:
        #     item = QListWidgetItem()
        #     self.window.lw_chat_history.addItem(item)
        #     item.setIcon(QIcon("images/foo.png"))
        #     item.setSizeHint(QSize(500, 500))

    def update_users_list_ui(self, users):
        self.window.lw_users.clear()
        for user in users:
            username = user["username"]
            self.color_table[username] = user["color"]
            self.window.lw_users.addItem(username)

    def send_chat(self):
        message = self.window.le_chat_input.text()
        if message:
            self.client.send_chat(self.user_id, self.session_id, message)
            self.window.le_chat_input.clear()

    def format_message(self, username: str, message: str) -> str:

        # Default color is black if username is not found
        color_code = self.color_table.get(username, "000000")

        message.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
        message.replace("\n", "<br>")

        # Create a QLabel to support rich text (HTML)
        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)  # For automatic detection

        if username == "system":
            message = f"<i>{message}</i>"
        label.setText(f"<b><span style='color:#{color_code}'>{username}:</span></b> {message}")

        # Create a QListWidgetItem and set the QLabel as its widget
        item = QListWidgetItem()
        self.window.lw_chat_history.addItem(item)
        self.window.lw_chat_history.setItemWidget(item, label)

        # Adjust the item size to match the label's content
        item.setSizeHint(label.sizeHint())

        # words = message.split()
        # words.insert(0, f"<{username}> ")
        # current_line, output_text = "", ""
        # for word in words:
        #     if len(current_line + word) <= 84:
        #         current_line += f"{word} "
        #     else:
        #         output_text += current_line + "\n"
        #         current_line = f"{word} "
        # output_text += current_line
        # return output_text

        return item

    def on_text_changed(self, message):
        if message.startswith("/"):
            filtered_commands = [cmd for cmd in self.commands if cmd.startswith(message)]
            self.completer.setModel(QStringListModel(filtered_commands))
        else:
            self.completer.setModel(QStringListModel([]))

    def eventFilter(self, source, event):
        if event.type() != QEvent.Close or source is not self.window:
            return super().eventFilter(source, event)  # Call the base class method for other events

        if not self.is_running:
            self.quit(event)
        reply = QMessageBox.question(
            self,
            "Warning",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.is_running = False
            self.quit(event)
        else:
            event.ignore()
        return True  # Indicate that the event was handled

    def quit(self, event):
        self.threadpool.waitForDone()
        event.accept()
        QApplication.quit()  # Quit the application


def main():
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication()
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
