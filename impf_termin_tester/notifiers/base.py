import abc


class NotificationService:
    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def initialize(self):
        pass

    def sent_notification(self, result):
        try:
            return self._sent_notification(result)
        except:
            return False

    @abc.abstractmethod
    def _sent_notification(self, result):
        return True
