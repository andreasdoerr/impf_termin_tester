import urllib3

from impf_termin_tester.notifiers import NotificationService


class PushSaferNotification(NotificationService):
    def __init__(self, private_key, https=None):
        """ Sent push notifications via the https://www.pushsafer.com/ API.
        
        This class allows for push notifications to any device. Registration
        for the pushsafer.com service is required. The `private_key` is available
        after creating a user account. Free trials are available. Paid
        packages are available for long-term use.
        The target device needs to have the pushsafer.com app installed in order
        to receive the push notifications.        

        Parameters
        ----------
        private_key : string
            Private key as generated in the pushsafer account.
        https : urllib3.PoolManger or urllib3.Proxymanager, optional
            A predefined Proxymanager can be given, e.g. for https requests
            from behing a proxy. The default is None.

        Returns
        -------
        None.

        """
        super().__init__(name="Push notification")

        self.private_key = private_key
        self.https = https

        self.pushsafer_url = "https://www.pushsafer.com/api"

    def initialize(self):
        self.https = self.https or urllib3.PoolManager()

    def _sent_notification(self, result):
        """ Sent out the pushsafer.com post request to trigger the notification """
        post_fields = {
            "t": "Appointment available!",
            "m": "Check website for more details.",
            "s": 25,
            "v": 3,
            "i": 1,
            "c": "#51eb2f",
            "d": "a",
            "u": result.url,
            "ut": "Link öffnen",
            "k": self.private_key,
            "pr": 2,
            "p": "data:image/png;base64," + result.screenshot,
        }
        request = self.https.request("POST", self.pushsafer_url, fields=post_fields)
        return request.status == 200
