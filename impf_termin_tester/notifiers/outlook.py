import win32com.client as win32

from impf_termin_tester.notifiers import NotificationService


class OutlookNotification(NotificationService):
    def __init__(self, target_email):
        super().__init__(name="Outlook e-mail client")
        self.target_email = target_email
        self.outlook = None

    def initialize(self):
        self.outlook = win32.Dispatch("outlook.application")

    def _sent_notification(self, result):
        mail = self.outlook.CreateItem(0)
        mail.To = self.target_email
        mail.Subject = "Appointment available"
        mail.Body = "Check " + result.url
        mail.Send()
        return True
