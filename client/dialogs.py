import os
import re
import markdown
import requests
from PySide6.QtWidgets import QDialog, QScrollArea, QLabel
from PySide6.QtCore import Qt
from PySide6.QtUiTools import QUiLoader


CUR_DIR = os.path.dirname(__file__)


class ServerTokens(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loader = QUiLoader()
        self._init_ui()

    def _init_ui(self):
        self.window = self.loader.load(os.path.join(CUR_DIR, "design", "server.ui"), self)


class Documentation(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.loader = QUiLoader()

        self._init_ui()

    def _init_ui(self):
        self.window = self.loader.load(os.path.join(CUR_DIR, "design","documentation.ui"), self)

        self.scroll_area = self.window.findChild(QScrollArea, "scrollArea")
        self.label = self.scroll_area.findChild(QLabel, "label")

        # Load and set the documentation text
        text = self.load_documentation()
        processed_text = self._process_markdown(text)
        self.label.setText(markdown.markdown(processed_text))
        self.label.setTextFormat(Qt.RichText)
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)

    def load_documentation(self):
        # Load the documentation from the README.md
        url = r"https://raw.githubusercontent.com/umyedi/chat-app/main/README.md"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return f"Could load the documentation on the url '{url}'."

    def _process_markdown(self, text: str) -> str:
        text = re.sub(r"```[a-z]*\n", "```\n", text)  # Remove code language identifiers
        html = markdown.markdown(text, extensions=["fenced_code"])  # Use 'fenced_code' extension for code blocks
        html = html.replace("<pre><code>", "<pre>").replace("</code></pre>", "</pre>")  # avoid nested formatting issues
        html = html.replace("<pre>", '<pre style="background-color:#D9D9D9;">')  # add code block background color
        return html