import os
import markdown
import requests
from PySide6.QtWidgets import QDialog, QScrollArea, QLabel
from PySide6.QtUiTools import QUiLoader


CUR_DIR = os.path.dirname(__file__)


class ServerTokens(QDialog):
    def __init__(self, parent=None, current_ip: str = None, current_port: str = None) -> None:
        super().__init__(parent)

        self.current_ip = current_ip
        self.current_port = current_port

        self.loader = QUiLoader()
        self._init_ui()

    def _init_ui(self) -> None:
        self.window = self.loader.load(os.path.join(CUR_DIR, "design", "server.ui"), self)
        self.window.ip_input.setText(self.current_ip)
        self.window.port_input.setText(self.current_port)


class Documentation(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.loader = QUiLoader()

        self._init_ui()

    def _init_ui(self) -> None:
        self.window = self.loader.load(os.path.join(CUR_DIR, "design", "documentation.ui"), self)

        self.scroll_area = self.window.findChild(QScrollArea, "scrollArea")
        self.label = self.scroll_area.findChild(QLabel, "label")

        text = self.load_documentation()
        self.label.setText(text)

    def load_documentation(self) -> str:
        url = r"https://raw.githubusercontent.com/umyedi/chat-app/main/README.md"
        response = requests.get(url)
        if response.status_code == 200:
            # Uses 'fenced_code' extension for code blocks formatting
            return markdown.markdown(response.text, extensions=["fenced_code"])
        return f"Couldn't load '{url}'."
