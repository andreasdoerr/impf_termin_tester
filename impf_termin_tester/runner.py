
import re
import time
import toml
import logging

from datetime import datetime


def get_valid_urls(urls, pattern, warning_message=None):
    # Default warning message if invalid URL is found in config file
    if warning_message is None:
        warning_message = "   Invalid URL in config file: {}."
        
    # Retrieve all valid URLs according to given regex pattern
    valid_urls = []
    for url in urls:
        # Sanitize input string
        url_processed = url.strip()
        match = re.match(pattern, url_processed)
        if match is None:
            logging.warn(warning_message.format(url))
        else:
            valid_urls.append(match.string)
    return valid_urls


def check_config(config):
    
    center_pattern = re.compile("https://\d{3}-iz\.impfterminservice\.de/impftermine/service\?plz=\d{5}")
    center_warning = "   Invalid vaccination center URL in config file: {}"
    center_urls = get_valid_urls(config['center_urls'], center_pattern, center_warning)
    
    appointment_pattern = re.compile("https://\d{3}-iz\.impfterminservice\.de/impftermine/suche/\w{4}-\w{4}-\w{4}/\d{5}")
    appointment_warning = "   Invalid vaccination center URL in config file: {}"
    appointment_urls = get_valid_urls(config['appointment_urls'], appointment_pattern, appointment_warning)
    
    return dict(center_urls=center_urls, appointment_urls=appointment_urls)


def read_config(config_file, default_config=None):    
    
    if default_config is None:
        default_config = dict()
    
    try:
        with open(config_file, 'r') as file:
            config = toml.load(file)
        config = check_config(config)
    except Exception as e:
        logging.error(f"   Could not read config from {config_file}.")
        logging.error(e)
        config = dict()
    
    # Do not alter the default config argument
    result_config = default_config.copy()
    
    # Update default config with data from config file
    result_config.update(config)

    assert "center_urls" in config or "appointment_urls" in config
    if "center_urls" in config:
        assert len(config["center_urls"]) > 0
    if "appointment_urls" in config:
        assert len(config["appointment_urls"]) > 0
    
    # Return new configuration
    return result_config


class Runner:
    def __init__(self, config_file, center_browser, appointment_browser, notifiers, test_notifiers=False):
        self.config_file = config_file
        self.config = dict()
        
        self.center_browser = center_browser
        self.appointment_browser = appointment_browser
        self.notifiers = notifiers

        self.test_notifiers = test_notifiers

        self.wait_time = 5
        self.interval_time = 1 * 60

    def start(self):
        self._initialize()
        self._run()

    def _initialize(self):
        logging.info("#" * 80)
        logging.info(" Setup")
        logging.info("-" * 80)
        
        logging.info(f" - Read configuration file.")
        self.config = read_config(self.config_file)
        if "center_urls" in self.config:
            n_centers = len(self.config["center_urls"])
            for i, center_url in enumerate(self.config["center_urls"]):
                logging.info(f"    * [{i+1} of {n_centers}]: Checking vaccination center {center_url}.")
        if "appointment_urls" in self.config:
            n_appointments = len(self.config["appointment_urls"])
            for i, appointment_url in enumerate(self.config["appointment_urls"]):
                logging.info(f"    * [{i+1} of {n_appointments}]: Checking for appointments with {appointment_url}.")
        logging.info("   Done")

        # Initialize browser
        logging.info(f" - Initialize: Browser.")
        self.center_browser.initialize()
        self.appointment_browser.initialize()
        logging.info("   Done")

        # Initialize all notification channels
        for notifier in self.notifiers:
            logging.info(f" - Initialize notification channel: {notifier.name}")
            notifier.initialize()
            logging.info("   Done")

        # Test all notification channels (if enabled)
        if self.test_notifiers:
            result = self.browser.get_dummy_result()
            self.sent_notifications(result, "Test notification channel")
        else:
            logging.info(" - Notification channel test disabled.")

        logging.info("#" * 80)
        logging.info("")

    def sent_notifications(self, result, label="Sent notification"):
        for notifier in self.notifiers:
            logging.info(f" - {label}: {notifier.name}")
            success = notifier.send_notification(result)
            if success:
                logging.info("   Success.")
            else:
                logging.info("   Failed.")

    def _run_url(self, url, browser):
        result = browser.check_url(url)

        if result is None:
            logging.info("   RESULT: No appointments available.")
            return

        logging.info("*" * 80)
        logging.info("   RESULT: Appointments available")
        logging.info("*" * 80)
        self.sent_notifications(result)
        logging.info("*" * 80)

    def _run(self):
        while True:
            logging.info("#" * 80)
            logging.info("Checking websites:")
            logging.info(datetime.now().strftime("%d.%m.%Y - %H:%M"))
            logging.info("-" * 80)
            
            logging.info(f" - Read configuration file.")
            self.config = read_config(self.config_file)
            logging.info("   Done")

            if "center_urls" in self.config:
                center_urls = self.config["center_urls"]
                n_centers = len(center_urls)
                logging.info("-" * 80)
                logging.info(f" Check available vacination center registration codes.")
                logging.info("-" * 80)
                for i, url in enumerate(center_urls):
                    try:
                        logging.info(f" - [{i+1} of {n_centers}], open: {url}")
                        self._run_url(url, self.center_browser)
                    except Exception as e:
                        logging.info(f"   Failed {e}")
                    time.sleep(self.wait_time)

            if "center_urls" in self.config:
                appointment_urls = self.config["appointment_urls"]
                n_appointments = len(appointment_urls)
                logging.info("-" * 80)
                logging.info(f" Check available appointments.")
                logging.info("-" * 80)
                for i, url in enumerate(appointment_urls):
                    try:
                        logging.info(f" - [{i+1} of {n_appointments}], open: {url}")
                        self._run_url(url, self.appointment_browser)
                    except Exception as e:
                        logging.info(f"   Failed {e}")
                    time.sleep(self.wait_time)
                
            logging.info("-" * 80)
            logging.info("Checking completed.")
            logging.info("#" * 80)
            logging.info("")

            logging.info(f"Wait {self.interval_time // 60}min\n")
            time.sleep(self.interval_time)
