"""

Ce fichier gère le code coté client.

"""

from time import sleep
import json
import zmq


class Client:
    def __init__(self, ip: str, port: str, timeout: int = 5000) -> None:
        self.server_address = f"tcp://{ip}:{port}"

        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, timeout)
        self.socket.connect(self.server_address)

    def send_request(self, request: dict):
        # self.socket.send(str(request).encode("utf-8"))
        self.socket.send(json.dumps(request).encode("utf-8"))
        
        try:
            response = self.socket.recv().decode("utf-8")
            return json.loads(response)
        except zmq.Again:
            return {"status": "error", "message": "Request timed out"}
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid response format"}

    def join_game(self, game_id, username):
        request = {"action": "join_game", "params": {"game_id": game_id, "username": username}}
        return self.send_request(request)

    def get_game_status(self, game_id, user_id):
        request = {"action": "get_game_status", "params": {"user_id": user_id, "game_id": game_id}}
        return self.send_request(request)

    def send_message(self, user_id, game_id, message):
        request = {
            "user_id": user_id,
            "action": "send_message",
            "params": {"user_id": user_id, "game_id": game_id, "message": message},
        }
        return self.send_request(request)


if __name__ == "__main__":
    client = Client(ip="10.246.203.143", port="5555")
