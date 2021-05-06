import time
import logging
from collections import namedtuple
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class Browser:

    Result = namedtuple("Result", ["source", "screenshot", "time", "url"])

    def __init__(self, binary_location, chrome_driver):
        # Path to chrome executable and chrome driver executable
        self.binary_location = binary_location
        self.chrome_driver = chrome_driver

        # x-path for elements on the website
        self.cookie_xpath = "/html/body/app-root/div/div/div/div[2]/div[2]/div/div[2]/a"
        self.button_xpath = "/html/body/app-root/div/app-page-its-search/div/div/div[2]/div/div/div[5]/div/div[1]/div[2]/div[2]/button"

    def initialize(self):
        opts = Options()
        opts.binary_location = self.binary_location
        self.driver = webdriver.Chrome(options=opts, executable_path=self.chrome_driver)
        self.driver.set_window_size(1400, 1050)

    def check_url(self, url):
        # Open website
        self.driver.get(url)
        time.sleep(3)

        # Accept cookies if available
        try:
            cookie_button = self.driver.find_element_by_xpath(self.cookie_xpath)
            cookie_button.click()
            logging.info("   ACTION: Acknowledge cookies.")
            time.sleep(3)
            logging.info("   ACTION: Reload website")
            self.driver.get(url)
            logging.info("           Done")
            time.sleep(3)
        except NoSuchElementException:
            pass

        # Click appointment button
        submit_button = self.driver.find_elements_by_xpath(self.button_xpath)
        if len(submit_button) != 1:
            logging.info(f"   WARNING: Found {len(submit_button)} buttons.")
            return None
        else:
            logging.info("   ACTION: Click button.")
            submit_button[0].click()
            time.sleep(3)

        # Check if no appointment text visible
        source = self.driver.page_source
        if source.find("Derzeit stehen leider keine Termine zur Verfügung") >= 0:
            return None

        # Take screenshot
        screenshot = self.driver.get_screenshot_as_base64()

        # Current time
        current_time = datetime.now()

        # Return result object
        result = self.Result(
            source=source, screenshot=screenshot, time=current_time, url=url
        )
        return result
