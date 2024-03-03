import zmq
import traceback
from PySide6.QtCore import QThread, Signal


class Client(QThread):
    received_message = Signal(str)

    def __init__(self, ip: str = "127.0.0.1", port: str = "5555"):
        super().__init__()
        self.address = None
        self.context = None
        self.socket = None
        self.is_running = False
        self._set_address_and_connect(ip, port)

    def _set_address_and_connect(self, ip: str, port: str):
        if self._set_address(ip, port):
            self._initialize_socket()

    def _set_address(self, ip: str, port: str):
        string = ip.split(".")
        if len(string) != 4:
            return False
        for byte in string:
            if not byte.isdigit():
                return False
            elif not (0 <= int(byte) <= 255):
                return False
        if not port.isdigit():
            return False

        self.address = f"tcp://{ip}:{port}"
        return True

    def _initialize_socket(self):
        if self.context is not None:
            self.context.term()
        self.context = zmq.Context()
        if self.socket is not None:
            self.socket.close()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(self.address)

    def run(self):
        while self.is_running:
            try:
                message = self.socket.recv()
                self.received_message.emit(message.decode())
            except zmq.Again:  # No message received, sleep briefly to yield execution and reduce CPU usage
                self.sleep(1)
            except zmq.ContextTerminated:  # Catches the termination of the context and exits the loop
                break
            except zmq.ZMQError as e:
                print(f"Error: {e}")
                print(f"Traceback: {traceback.format_exc()}")

    def restart(self, new_ip: str, new_port: str):
        self.is_running = False  # Stop the current listening loop
        self.socket.close()  # Close the current socket
        self.context.term()  # Terminate the current context
        self._set_address_and_connect(new_ip, new_port)  # Set the new address and connect
        self.start()  # Restart the listening thread

    def stop(self):
        self.is_running = False
        self.socket.close()  # Close the ZMQ socket
        self.context.term()  # Terminate the ZMQ context
        self.wait()  # Wait for the thread to finish
