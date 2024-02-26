"""

Ce fichier gère les données récupérer depuis le serveur par le client.

"""

from PySide6.QtCore import Signal, QObject, QThread
from client import Client


class Worker(QObject):

    update_users_signal = Signal(list)
    update_chat_signal = Signal(dict)

    def __init__(self, client: Client, session_id: str, user_id: str):
        super().__init__()
        self.client = client
        self.session_id = session_id
        self.user_id = user_id
        self.is_running = False

    def run(self):
        """Main function of the worker that will be executed in the thread.

        Raises:
            Exception: An error occured with the server.
        """
        self.is_running = True
        while self.is_running:

            response = self.client.get_game_status(self.session_id, self.user_id)

            if response["status"] == "error":
                self.stop()
                raise ValueError(response["message"])
            else:

                # Data retrieving
                chat_history = response.get("data", {}).get("chat_history", [])
                users = response.get("data", {}).get("users", [])

                # Use of signal
                self.update_users_signal.emit(users)
                self.update_chat_signal.emit(chat_history)

            QThread.sleep(1)  # Shouldn't go below 1 second

    def stop(self):
        self.is_running = False