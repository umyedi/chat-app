import zmq
import traceback
from PySide6.QtCore import QThread, Signal


class Client(QThread):
    received_message = Signal(str)

    def __init__(self, ip: str = "127.0.0.1", port: str = "5555") -> None:
        super().__init__()

        self.ip = ip
        self.port = port
        self.address = None

        self.context = None
        self.socket = None
        self.is_running = False

        self._set_address_and_connect(ip, port)

    def _set_address_and_connect(self, ip: str, port: str) -> None:
        if self._set_address(ip, port):
            self._initialize_socket()

    def _set_address(self, ip: str, port: str) -> bool:
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

        self.ip, self.port = ip, port
        self.address = f"tcp://{self.ip}:{self.port}"
        return True

    def _initialize_socket(self) -> None:
        if self.context is not None:
            self.context.term()

        if self.socket is not None:
            self.socket.close()

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(self.address)

    def _wait_thread_to_close(self) -> None:
        self.is_running = False
        self.socket.close()
        self.context.term()
        self.wait()

    def run(self) -> None:
        self.is_running = True
        while self.is_running:
            try:
                message = self.socket.recv()
                self.received_message.emit(message.decode())
            except zmq.ContextTerminated:
                break
            except zmq.ZMQError as e:
                print(f"Error: {e}")
                print(f"Traceback: {traceback.format_exc()}")

    def restart(self, new_ip: str, new_port: str) -> None:
        self._wait_thread_to_close()
        self._set_address_and_connect(new_ip, new_port)
        self.start()

    def stop(self) -> None:
        self._wait_thread_to_close()
