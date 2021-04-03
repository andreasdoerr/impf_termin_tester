import abc


class NotificationService:
    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def initialize(self):
        pass

    def send_notification(self, result):
        try:
            return self._send_notification(result)
        except:
            return False

    @abc.abstractmethod
    def _send_notification(self, result):
        return True
