from impf_termin_tester.utils.send_mail import send_mail

from impf_termin_tester.notifiers import NotificationService


class MailNotification(NotificationService):
    def __init__(self, target_email, mail_server, login_user=None, login_password=None):
        super().__init__(name="SMTP e-mail client")
        self.target_email = target_email
        self.mail_server = mail_server
        self.login_user = login_user
        self.login_password = login_password

    def initialize(self):
        pass

    def _send_notification(self, result):
        ok, msg = send_mail(
            mail_from=self.target_email,
            to=[self.target_email],
            subject="Appointment available",
            text="Check " + result.url,
            mail_server=self.mail_server,
            login_user=self.login_user,
            login_password=self.login_password,
        )

        return ok
