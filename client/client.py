"""

Ce fichier gère le code coté client.

"""

import json
import zmq


class Client:
    def __init__(self, ip: str, port: str, timeout: int = 2000) -> None:
        self.server_address = f"tcp://{ip}:{port}"
        self.timeout = timeout
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.socket.connect(self.server_address)

    def send_request(self, request: dict):

        try:
            self.socket.send(json.dumps(request).encode("utf-8"))
            response = self.socket.recv().decode("utf-8")
            return json.loads(response)
        except zmq.Again:
            self.reinitialize_socket()
            return {"status": "error", "message": "Request timed out"}        
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid response format"}
        except zmq.error.ZMQError:
            self.reinitialize_socket()
            return {"status": "error", "message": "Operation cannot be accomplished in current state"}
    
    def reinitialize_socket(self):
        """Close the existing socket and reinitialize it."""
        self.socket.close()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
        self.socket.connect(self.server_address)
    
    def join_game(self, session_id, username):
        request = {"action": "join_session", "params": {"session_id": session_id, "username": username}}
        return self.send_request(request)

    def get_game_status(self, session_id, user_id):
        request = {"action": "get_session_status", "params": {"user_id": user_id, "session_id": session_id}}
        return self.send_request(request)

    def send_chat(self, user_id, session_id, message):
        request = {
            "user_id": user_id,
            "action": "write_message",
            "params": {"user_id": user_id, "session_id": session_id, "message": message},
        }
        return self.send_request(request)
