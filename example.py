from impf_termin_tester.browser import Browser
from impf_termin_tester.runner import Runner

from impf_termin_tester.notifiers.pushsafer import PushSaferNotification
from impf_termin_tester.notifiers.outlook import OutlookNotification
from impf_termin_tester.notifiers.file import FileNotification


if __name__ == "__main__":

    # List of URLs to be checked
    urls = [
        "https://XXX-iz.impfterminservice.de/impftermine/suche/XXXX-XXXX-XXXX/YYYYY/"
    ]

    # Private key for push notifications via pushsafer.com
    pushsafer_private_key = "your_private_key"

    # Target for e-mail notifications
    email = "your_email_address"

    # Output directory for file dump
    output_dir = "output_folder_path"

    # Create notifiers
    notifiers = [
        PushSaferNotification(pushsafer_private_key),
        OutlookNotification(email),
        FileNotification(output_dir),
    ]

    # Communication with browser
    binary_location = "path_to_chrome.exe"
    chrome_driver = "path_to_chromedriver.exe"
    browser = Browser(binary_location, chrome_driver)

    runner = Runner(urls, browser, notifiers)
    runner.start()
