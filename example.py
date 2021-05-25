import logging

from impf_termin_tester.browser import Browser
from impf_termin_tester.runner import Runner

from impf_termin_tester.notifiers.mail import MailNotification
from impf_termin_tester.notifiers.pushsafer import PushSaferNotification
from impf_termin_tester.notifiers.file import FileNotification
from impf_termin_tester.notifiers.notify_run_wrapper import AndroidNotification


# OutlookNotification is based on pywin32 and thus Windows only
# Check README.md for setup instrunctions
# from impf_termin_tester.notifiers.outlook import OutlookNotification


if __name__ == "__main__":

    # Show information about current operation
    logging.basicConfig(level=logging.INFO)

    # List of URLs to be checked
    urls = [
        "https://XXX-iz.impfterminservice.de/impftermine/suche/XXXX-XXXX-XXXX/YYYYY/",
    ]

    # Private key for push notifications via pushsafer.com
    pushsafer_private_key = "your_private_key"

    # Target for e-mail notifications (used by OutlookNotification, MailNotification)
    email = "your_email_address"
    # Mail Server/Credentials (used by MailNotification)
    mail_server = "mail.example.org:587"
    login_user = "username"
    login_password = "password"

    # Output directory for file dump
    output_dir = "output_folder_path"

    # MQTT Broker
    broker = "address_of_your_mqtt_broker"

    # Create notifiers
    notifiers = [
        # AndroidNotification(), # See https://pypi.org/project/notify-run/ to setup the library, i.e., run ```notify-run register```
        # MailNotification(email, mail_server, login_user, login_password),
        # PushSaferNotification(pushsafer_private_key),
        # OutlookNotification(email),    # Windows only, requiers pywin32
        FileNotification(output_dir),
        # MQTTNotification(broker)
    ]

    # Communication with browser
    binary_location = "path_to_chrome.exe"
    chrome_driver = "path_to_chromedriver.exe"
    browser = Browser(binary_location, chrome_driver)

    runner = Runner(urls, browser, notifiers)
    runner.start()
