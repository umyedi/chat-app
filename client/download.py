import os
import requests
from pathlib import Path
from datetime import datetime


class DownloadManager:
    def __init__(self, folder_path: str, image_name_format: str = "%Y-%m-%d_%H-%M-%S") -> None:
        self.image_name_format = image_name_format
        self.folder_path = Path(folder_path).absolute()

    def _generate_image_name(self, suffix: str):
        timestamp = datetime.now().strftime(self.image_name_format)
        return f"{timestamp}.{suffix}"

    def download_image(self, image_url: str, suffix: str):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        image_path = os.path.join(self.folder_path, self._generate_image_name(suffix))
        response = requests.get(image_url)

        if response.status_code != 200:
            raise requests.exceptions.RequestException(response.status_code)

        with open(image_path, "wb") as file:  # Open the file in binary
            file.write(response.content)

        return image_path
