"""

Ce fichier gère le code coté serveur.

"""

from actions import Actions
from log import logger
import sys
import json
import zmq


class Server:
    def __init__(self, port: str = 5555) -> None:

        self.socket = zmq.Context().socket(zmq.REP)
        self.socket.bind(f"tcp://*:{port}")

        self.is_running = False

    def format_response(self, status: str = "success", message: str = "", data: dict = None) -> bytes:
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

    def run(self):
        """Runs a while loop that scans for client requests."""
        
        logger.info("Server started")
        self.is_running = True

        while self.is_running:
            try:
                client_message = self.socket.recv().decode("utf-8")
                request = json.loads(client_message)
                logger.debug(request)

                action = request.get("action")
                params = request.get("params", {})
                actions = Actions(params["session_id"])
                del params["session_id"]

                if actions.exists(action):
                    response_data = actions.execute(action, params)
                    response = self.format_response(data=response_data)
                else:
                    response = self.format_response(status="error", message="Action not found")
                
                self.socket.send(response)
                logger.debug(response)

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                self.socket.send(self.format_response(status="error", message="Invalid JSON format"))
            except KeyError as e:
                logger.error(f"Missing parameter: {str(e)}")
                self.socket.send(self.format_response(status="error", message=f"Missing parameter: {e}"))
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                self.socket.send(self.format_response(status="error", message=str(e)))

        logger.info("Server stopped")

    def stop(self):
        """Stops the while loop."""
        self.is_running = False

if __name__ == "__main__":
    try:
        Server().run()
    except KeyboardInterrupt:
        logger.info("Server stopped by KeyboardInterrupt")
        sys.exit(130)
