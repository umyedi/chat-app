"""

Ce fichier gère le code coté serveur.

"""

from actions import Actions
from filters import Filters
from log import logger
import sys
import json
import zmq


class Server:
    def __init__(self, port: int = 5555) -> None:

        self.socket = zmq.Context().socket(zmq.REP)
        self.socket.bind(f"tcp://*:{port}")

        self.filters = Filters()

    def _format_response(self, status: str = "success", message: str = "", data: dict = None) -> bytes:
        """Format the response to be sent back to the client.

        Args:
            status (str, optional): Status of the response ('success' or 'error'). Defaults to "success".
            message (str, optional): Reponse message to be sent to the client. Defaults to None.
            data (dict, optional): Data to be sent to the client. Defaults to None.

        Returns:
            bytes: Formatted response
        """
        response = {"status": status, "message": message}
        if data is not None:
            response["data"] = data
        return json.dumps(response).encode("utf-8")

    def _process_request(self, client_message: str) -> dict:
        """Check the client message validity and return the data the client asked for.

        Args:
            client_message (str): message of the client

        Returns:
            dict: result of the client request
        """
        try:
            request = json.loads(client_message)
            logger.debug(request)

            action = request.get("action")
            params = request.get("params", {})
            self.filters.remove_inactive_users(params["session_id"])
            return self._handle_action(action, params)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return self._format_response(status="error", message="Invalid JSON format")
        except ValueError as e:
            logger.error(f"{str(e)}")
            return self._format_response(status="error", message=str(e))
        except KeyError as e:
            logger.error(f"Missing parameter: {str(e)}")
            return self._format_response(status="error", message=f"Missing parameter: {e}")

    def _handle_action(self, action: str, params: dict) -> dict:
        """Runs the action provided with the provided parameters.

        Args:
            action (str): keyword corresponding to an action
            params (dict): parameters needed for this action

        Returns:
            dict: result of the action
        """
        actionHandler = Actions(params["session_id"])
        if actionHandler.exists(action):
            data = actionHandler.execute(action, params)
            return self._format_response(data=data)
        else:
            return self._format_response(status="error", message="Action not found")

    def run(self) -> None:
        """Runs a while loop that scans for clients messages."""

        logger.info("Server started")
        while True:
            try:
                client_message = self.socket.recv().decode("utf-8")
                response = self._process_request(client_message)
                self.socket.send(response)
                logger.debug(response)
            except Exception as e:
                logger.error(str(e))
                self.socket.send(self._format_response(status="error", message="An unexpected error occurred"))




def main():
    try:
        Server().run()
    except KeyboardInterrupt:
        logger.info("Server stopped by KeyboardInterrupt")
        sys.exit(130)


if __name__ == "__main__":
    main()
