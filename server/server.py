"""

Ce fichier gère le code coté serveur.

"""


from server.utils import get_game_status
from server.logging import logger
import sys
import os
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

actions = {"get_game_status": get_game_status}


def main():

    while True:
        message = socket.recv().decode("utf-8")
        request = eval(message)
        logger.info(f"(server.main)request={request}")

        try:
            action = request.get("action")
            params = request.get("params", {})

            if action in actions:
                function = actions[action]
                response = function(**params)
            else:
                response = {"status": "error", "message": "Action not found"}

            socket.send(str(response).encode("utf-8"))
            logger.info(f"(server.main)response={response}")

        except Exception as e:
            logger.error("(server.main)" + str(e))
            socket.send(str({"status": "error", "message": e}).encode("utf-8"))


if __name__ == "__main__":
    try:
        logger.info("Server opened.")
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped.")
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
