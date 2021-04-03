import os
import base64
from PIL import Image
from io import BytesIO

from impf_termin_tester.notifiers import NotificationService


class FileNotification(NotificationService):
    def __init__(self, output_dir):
        super().__init__(name="Save to file")
        self.output_dir = output_dir

    def initialize(self):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    def _send_notification(self, result):
        # Create unique filename with registration code and time
        code_str = result.url.strip("/").split("/")[-2].replace("-", "_")
        date_str = result.time.strftime("%Y%m%d_%H%M")

        # Write website HTML file to disk
        file_name = f"{date_str}_{code_str}.html"
        file_path = os.path.join(self.output_dir, file_name)
        with open(file_path, "w") as file:
            file.write(result.source)

        # Write website screenshot to disk
        file_name = f"{date_str}_{code_str}.png"
        file_path = os.path.join(self.output_dir, file_name)
        screenshot = Image.open(BytesIO(base64.b64decode(result.screenshot)))
        with open(file_path, "w") as file:
            screenshot.save(file_path, "PNG")

        return True
