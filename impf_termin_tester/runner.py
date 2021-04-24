import time
import logging

from datetime import datetime


class Runner:
    def __init__(self, urls, browser, notifiers):
        self.urls = urls
        self.browser = browser
        self.notifiers = notifiers

        self.wait_time = 5
        self.interval_time = 10 * 60

    def start(self):
        self._initialize()
        self._run()

    def _initialize(self):
        logging.info("#" * 80)
        logging.info(" Setup")
        logging.info("-" * 80)

        # Initialize browser
        logging.info(f" - Initialize: Browser ...", end=" ")
        self.browser.initialize()
        logging.info("Done")

        # Initialize all notification channels
        for notifier in self.notifiers:
            logging.info(f" - Initialize notification channel: {notifier.name}")
            notifier.initialize()
            logging.info("   Done")

        logging.info("#" * 80)
        logging.info("")

    def _run_url(self, url):
        result = self.browser.check_url(url)

        if result is None:
            logging.info("   RESULT: No appointments available.")
            return

        logging.info("*" * 80)
        logging.info("   RESULT: Appointments available")
        logging.info("*" * 80)

        for notifier in self.notifiers:
            logging.info(f" - Sent notification: {notifier.name}")
            success = notifier.send_notification(result)
            if success:
                logging.info("   Success.")
            else:
                logging.info("   Failed.")
        logging.info("*" * 80)

    def _run(self):
        while True:
            logging.info("#" * 80)
            logging.info("Checking websites:")
            logging.info(datetime.now().strftime("%d.%m.%Y - %H:%M"))
            logging.info("-" * 80)

            for i, url in enumerate(self.urls):
                try:
                    logging.info(f" - {i+1} of {len(self.urls)}, open: {url}")
                    self._run_url(url)
                except Exception as e:
                    logging.info(f"   Failed {e}")

                time.sleep(self.wait_time)

            logging.info("-" * 80)
            logging.info("Checking completed.")
            logging.info("#" * 80)
            logging.info("")

            logging.info(f"Wait {self.interval_time // 60}min\n")
            time.sleep(self.interval_time)
