import abc
import logging


class NotificationService:
    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def initialize(self):
        pass

    def send_notification(self, result):
        try:
            return self._send_notification(result)
        except Exception as e:
            logging.error(f"   Error: {e}")
            return False

    @abc.abstractmethod
    def _send_notification(self, result):
        return True
