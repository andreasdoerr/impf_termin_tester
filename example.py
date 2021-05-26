import logging

from impf_termin_tester.browser import Browser, Browser_Get_Code
from impf_termin_tester.runner import Runner

# Import one or multiple of the available notification channels
# from impf_termin_tester.notifiers.mail import MailNotification
# from impf_termin_tester.notifiers.pushsafer import PushSaferNotification
# from impf_termin_tester.notifiers.file import FileNotification
# from impf_termin_tester.notifiers.notify_run_wrapper import AndroidNotification
# from impf_termin_tester.mqtt import MQTTNotification
# OutlookNotification is based on pywin32 and thus Windows only
# Check README.md for setup instrunctions
# from impf_termin_tester.notifiers.outlook import OutlookNotification


if __name__ == "__main__":

    # Show information about current operation
    logging.basicConfig(level=logging.INFO)
    
    # #########################################################################
    # General Configuration
    # #########################################################################
    
    # Config file with URLs (cf. example.toml)
    config_file = "path_to_toml_configuration_file"
    
    # Personal information for registration code retrieval
    age = 40
    email = "your_email_address"
    # ATTENTION: remove leading 0 (i.e. +49 you_mobile_number needs to be a valid phone number)
    phone = "your_mobile_number"
    personal_information = dict(age=age, email=email, phone=phone)
    
    # Enable/disable initial test of all notification channels
    test_notifiers = True

    # #########################################################################
    # Setup notification channels
    # #########################################################################

    # # Push notifications via pushsafer.com
    # private_key = "your_private_key"
    # push_notifier = PushSaferNotification(private_key)
    
    # # E-mail notifications via Outlook
    # email = "your_email_address"
    # outlook_notifier = OutlookNotification(email)
    
    # # E-mail notification via mail server
    # email = "your_email_address"
    # mail_server = "mail.example.org:587"
    # login_user = "username"
    # login_password = "password"
    # email_notifier = MailNotification(email, mail_server, login_user, login_password)
    
    # # File dump notification
    # output_dir = "output_folder_path"
    # file_notifier = FileNotification(output_dir)

    # # MQTT Broker notification
    # broker = "address_of_your_mqtt_broker"
    # mqtt_notifier = MQTTNotification(broker)
    
    # # Android push notification via https://pypi.org/project/notify-run/
    # android_notifier = AndroidNotification()

    # Create list of your notifiers, for example
    # notifiers = [
    #     push_notifier,
    #     outlook_notifier,
    #     email_notifier,
    #     file_notifier,
    #     mqtt_notifier,
    #     android_notifier,
    # ]
    notifiers = []

    # Communication with browser
    binary_location = "path_to_chrome.exe"
    chrome_driver = "path_to_chromedriver.exe"    
    center_browser = Browser_Get_Code(
        binary_location,
        chrome_driver,
        use_tabs=True,
        personal_information=personal_information
    )
    appointment_browser = Browser(binary_location, chrome_driver, use_tabs=True)


    runner = Runner(
        config_file,
        center_browser,
        appointment_browser,
        notifiers,
        test_notifiers=test_notifiers
    )
    runner.start()
