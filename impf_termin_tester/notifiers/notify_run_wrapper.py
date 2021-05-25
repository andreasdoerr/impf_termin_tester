import os
import base64
from io import BytesIO

from PIL import Image

from notify_run import Notify
from impf_termin_tester.notifiers import NotificationService


class AndroidNotification(NotificationService):
    def __init__(self):
        super().__init__(name="Send Android Push")
        self.notifier = Notify()

    def initialize(self):
        self.notifier.send("Impftermin Startup Test Message")

    def _send_notification(self, result):
        self.notifier.send(result.url)
        return True
