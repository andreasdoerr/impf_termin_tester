import logging

from impf_termin_tester.browser import Browser_Get_Code
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
        # "https://XXX-iz.impfterminservice.de/impftermine/service?plz=XXXXX/",
        "https://001-iz.impfterminservice.de/impftermine/service?plz=70376",
        "https://229-iz.impfterminservice.de/impftermine/service?plz=71065",
        "https://229-iz.impfterminservice.de/impftermine/service?plz=70629",
        "https://002-iz.impfterminservice.de/impftermine/service?plz=71297",
        "https://005-iz.impfterminservice.de/impftermine/service?plz=71636",
        "https://229-iz.impfterminservice.de/impftermine/service?plz=73037",



    ]

    # your age
    age = 35

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

    # Create notifiers
    notifiers = [
        AndroidNotification(), # See https://pypi.org/project/notify-run/ to setup the library, i.e., run ```notify-run register```
        # MailNotification(email, mail_server, login_user, login_password),
        # PushSaferNotification(pushsafer_private_key),
        # OutlookNotification(email),    # Windows only, requiers pywin32
        FileNotification(output_dir),
    ]

    # Communication with browser
    binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    chrome_driver = "/Users/chris/Downloads/chromedriver-2"
    browser = Browser_Get_Code(binary_location, chrome_driver, age)

    runner = Runner(urls, browser, notifiers)
    runner.start()
