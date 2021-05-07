import time
import logging
from collections import namedtuple
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys



class Browser:

    Result = namedtuple("Result", ["source", "screenshot", "time", "url"])
    Tab = namedtuple("Tab", ["url", "window_handle"])

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
        self.driver.set_window_size(400, 700)

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
    




class Browser_Get_Code(Browser):
    
    def __init__(self, binary_location, chrome_driver, age):
        super().__init__(binary_location, chrome_driver)

        self.check_button_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[2]/div/div/label[2]/span"
        # self.eligible_button_xpath ="/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/app-corona-vaccination-no/form/div[1]/div/div/label[1]"
        self.eligible_button_xpath ="/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/app-corona-vaccination-no/form/div[1]/div/div/label[1]/span"
        self.input_age_field_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/app-corona-vaccination-no/form/div[3]/div/div/input"
        self.perform_check_button_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/app-corona-vaccination-no/form/div[4]/button"
        # self.check_button_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[2]/div/div/label[2]/input"
        self.tab_list = []
        self.age = age


    def check_url(self, url):
        has_opened = False
        for tab in self.tab_list:
            if tab.url == url:
                has_opened = True
                self.driver.switch_to.window(tab.window_handle)
                break
        
        if not has_opened:
            if len(self.tab_list) > 0:
                script_str =  '''window.open(\"'''+ url + '''\" ,\"_blank\");'''
                # self.driver.find_element_by_css_selector("body").send_keys(Keys.COMMAND + "t")
                self.driver.execute_script(script_str)
            else:
                # Open website
                self.driver.get(url)

            # self.tab_list.append(self.Tab(url=url, window_handle=self.driver.current_window_handle))
            self.tab_list.append(self.Tab(url=url, window_handle=self.driver.window_handles[-1]))

        
        
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
        check_button = self.driver.find_elements_by_xpath(self.check_button_xpath)
        # check_button = self.driver.find_elements_by_xpath("button")
        

        if len(check_button) != 1:
            logging.info(f"   WARNING: Found {len(submit_button)} buttons.")
            return None
        else:
            logging.info("   ACTION: Click button.")
            check_button[0].click()
            time.sleep(3)


        source = self.driver.page_source
        is_waiting = True
        while is_waiting == True:
            time.sleep(1)
            if source.find("Bitte Warten") < 0:
                is_waiting = False
                

        # Check if no appointment text visible
        source = self.driver.page_source
        if source.find("Gehören Sie einer impfberechtigten Personengruppen an?") < 0:
            return None

        
        
        self.driver.find_elements_by_xpath(self.eligible_button_xpath)[0].click()
        time.sleep(1)
        self.driver.find_element_by_xpath(self.input_age_field_xpath).send_keys(Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE)
        self.driver.find_element_by_xpath(self.input_age_field_xpath).send_keys(str(age))
        time.sleep(1)
        self.driver.find_elements_by_xpath(self.perform_check_button_xpath)[0].click()

        # Take screenshot
        screenshot = self.driver.get_screenshot_as_base64()

        # Current time
        current_time = datetime.now()

        # Return result object
        result = self.Result(
            source=source, screenshot=screenshot, time=current_time, url=url
        )
        return result
    