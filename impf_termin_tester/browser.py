import time
import logging
from collections import namedtuple, defaultdict
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


class Browser:

    Result = namedtuple("Result", ["source", "screenshot", "time", "url"])

    def __init__(self, binary_location, chrome_driver, use_tabs=True):
        # Path to chrome executable and chrome driver executable
        self.binary_location = binary_location
        self.chrome_driver = chrome_driver

        self.tabs = dict()
        self.use_tabs = use_tabs
        
        self.found_time = dict()
        self.repeated_notifications = False

        # x-path for elements on the website
        self.cookie_xpath = "/html/body/app-root/div/div/div/div[2]/div[2]/div/div[2]/a"
        self.button_xpath = "/html/body/app-root/div/app-page-its-search/div/div/div[2]/div/div/div[5]/div/div[1]/div[2]/div[2]/button"
        self.cancel_xpath = "/html/body/app-root/div/app-page-its-search/app-its-search-slots-modal/div/div/div/div[2]/div/div/form/div[2]/button[2]"
        self.button_choose_xpath = "/html/body/app-root/div/app-page-its-search/app-its-search-slots-modal/div/div/div/div[2]/div/div/form/div[2]/button[1]"
        self.select_bw_xpath = "/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[3]/app-corona-vaccination-center/div[1]/label/span[2]/span[1]/span"
        self.select_center_xpath = "/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[3]/app-corona-vaccination-center/div[2]/label/span[2]/span[1]/span/span[1]"
        self.select_center_xpath = "/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[3]/app-corona-vaccination-center/div[2]/label/span[2]/span[1]/span"
        self.goto_center_xpath = "/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[4]/button"
        
        # Strings displayed if no appointment is available
        self.no_appointment_messages = [
            "Derzeit stehen leider keine Termine zur Verfügung",
            "Virtueller Warteraum des Impfterminservice",
            "Wir aktualisieren zurzeit das System. Bitte probieren Sie es in einigen Minuten erneut.",
        ]
        
        # Wait time for loading a new page
        self.time_loading = 2
        self.time_search_max = 10
        self.time_search_interval = 1
        self.time_keep_result = 12 * 60
        

    def initialize(self):
        opts = Options()
        opts.binary_location = self.binary_location
        self.driver = webdriver.Chrome(options=opts, executable_path=self.chrome_driver)
        self.driver.set_window_size(1400, 1050)         

    def check_url(self, url):
        """ Check if appointment is available
        

        Parameters
        ----------
        url : string
            URL for appointment check (including the registration code)

        Returns
        -------
        None or dict
            Returns None if no appointment is available. Otherwise a result dict
            is returned with page-source, time, screenshot and url.

        """
        # Open URL in browser
        self._open_url(url)
        
        # Handle cookie acceptance window
        self._handle_cookies(url)
        
        # Handle unwanted redirect to main website
        self._handle_redirect(url)
        
        # Check if appointments are available for selection
        if self.driver.find_elements_by_xpath(self.button_choose_xpath):
            choose_button = self.driver.find_element_by_xpath(self.button_choose_xpath)
            if choose_button.is_enabled():
                return self._get_result(url)

        # Click button to check for appointments
        if self.driver.find_elements_by_xpath(self.button_xpath):
            submit_button = self.driver.find_element_by_xpath(self.button_xpath)
            logging.info("   ACTION: Click button.")
            submit_button.click()
            time.sleep(2)

        # Wait for system to display appointments
        time_waited = 0
        while self.driver.page_source.find("Termine werden gesucht") >= 0:
            logging.info("   Info: Waiting for system to find appointment.")
            time.sleep(self.time_search_interval)
            time_waited += self.time_search_interval
            if time_waited > self.time_search_max:
                logging.info("   Info: Maximum waiting time exceeded.")
                break

        # Return None if website shows no available appointments
        source = self.driver.page_source
        for message in self.no_appointment_messages:
            if source.find(message) >= 0:
                return None

        return self._get_result(url)

    def get_dummy_result(self, dummy_url="http://www.google.com"):       
        """ Create result tuple for a dummy website
        """
        
        # Load dummy website
        self._open_url(dummy_url)
        # Return result dict
        return self._get_result(dummy_url)
  
    def _switch_to_url(self, url):
        """ Switch to the tab of a URL 
        
        If tabs are disabled the URL is opened in the current window.
        If no tab is opened for this URL, a new one is created.
        """
        
        # Tabs are disabled, open URL in current window
        if not self.use_tabs:
            self._open_url(url)
            return
            
        # Check if tab for URL is available
        if url in self.tabs:
            self.driver.switch_to.window(self.tabs[url])
            
    def _open_url(self, url):
        """ Open a given URL in the browser 
        
        If tabs are enabled, each URL is opened in a separate window.
        If the URL is already opened in a tab, this tab is reused.
        """
        
        # Open URL in current window if use of tabs is disabled
        if not self.use_tabs:
            self.driver.get(url)
            time.sleep(self.time_loading)
            return
        
        if url in self.tabs:
            # Switch to existing tab if URL has been opened before
            self.driver.switch_to.window(self.tabs[url])
            self.driver.get(url)
        else:
            # Create new tab if URL has not been opened before
            script_str = f"window.open(\"{url}\" ,\"_blank\");"
            self.driver.execute_script(script_str)
            self.tabs[url] = self.driver.window_handles[-1]
            self._open_url(url)
            
        time.sleep(self.time_loading)
    
    def _get_result(self, url):
        
        # Reset previous found if long ago
        if url in self.found_time:
            t0 = self.found_time[url]
            t1 = datetime.now()
            delta = t1 - t0
            if delta.total_seconds() > self.time_keep_result:
                self.found_time.pop(url)
        
        # Get page source
        source = self.driver.page_source
        # Take screenshot
        screenshot = self.driver.get_screenshot_as_base64()
        # Current time
        current_time = datetime.now()

        # Return result object
        result = self.Result(
            source=source, screenshot=screenshot, time=current_time, url=url
        )
        
        # If previously found, only return result again if requested
        if url in self.found_time:
            if self.repeated_notifications:
                return result
            else:
                return None
        
        # Not yet found, return result in any case
        self.found[url] = datetime.now()
        return result

    def _handle_cookies(self, url):
        # Accept cookies if available
        try:        
            cookie_button = self.driver.find_element_by_xpath(self.cookie_xpath)
            
            logging.info("   ACTION: Acknowledge cookies.")
            cookie_button.click()
            time.sleep(1)
            
            logging.info("   ACTION: Reload desired website")
            self._open_url(url)
            logging.info("           Done")
        except NoSuchElementException:
            pass
        
    def _handle_redirect(self, url):
        """ Handle sporadic redirect to main website """
        try:
            state_dropdown = self.driver.find_element_by_xpath(self.select_bw_xpath)
            center_dropdown = self.driver.find_element_by_xpath(self.select_center_xpath)
            goto_button = self.driver.find_element_by_xpath(self.goto_center_xpath)
            
            logging.info("   ACTION: Found redirection to main website.")

            # Select random center            
            state_dropdown.click()
            state_dropdown.send_keys(Keys.ENTER)
            center_dropdown.click()
            center_dropdown.send_keys(Keys.ENTER)
            goto_button.click()
            
            logging.info("   ACTION: Reload desired website")
            self._open_url(url)
            logging.info("           Done")
        except NoSuchElementException:
            pass
        
    def _page_contains(self, text):
        return self.driver.page_source.find(text) >= 0
    

class Browser_Get_Code(Browser):
    
    def __init__(
        self,
        binary_location,
        chrome_driver,
        use_tabs=False,
        personal_information=dict(),
    ):
        super().__init__(binary_location, chrome_driver, use_tabs)

        self.check_button_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[2]/div/div/label[2]/span"
        self.eligible_button_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/app-corona-vaccination-no/form/div[1]/div/div/label[1]/span"
        self.input_age_field_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/app-corona-vaccination-no/form/div[3]/div/div/input"
        self.perform_check_button_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/app-corona-vaccination-no/form/div[4]/button"
        self.input_email_field_xpath = "/html/body/app-root/div/app-page-its-check-result/div/div/div[2]/div/div/div/div/app-its-check-success/div/form/div[1]/label/input"
        self.input_phone_field_xpath = "/html/body/app-root/div/app-page-its-check-result/div/div/div[2]/div/div/div/div/app-its-check-success/div/form/div[2]/label/div/input"
        self.final_submit_xpath = "/html/body/app-root/div/app-page-its-check-result/div/div/div[2]/div/div/div/div/app-its-check-success/div/form/div[3]/button"

        self.personal_information = personal_information

    def check_url(self, url):
        
        # Switch to corresponding tab        
        self._switch_to_url(url)
        if self._page_contains("SMS Verifizierung"):
            logging.info(f"   Please enter the SMS verification code.")
            return self._get_result(url)

        # Open URL in browser
        self._open_url(url)
        
        # Handle cookie acceptance window
        self._handle_cookies(url)
        
        # Handle unwanted redirect to main website
        self._handle_redirect(url)

        # Click first check for eligibility button
        check_button = self.driver.find_elements_by_xpath(self.check_button_xpath)

        if len(check_button) != 1:
            logging.info(f"   WARNING: Found {len(check_button)} buttons.")
            return None
        else:
            logging.info("   ACTION: Click button.")
            check_button[0].click()
            time.sleep(1)

        # Wait for the system to check availability
        while self.driver.page_source.find("Bitte warten") >= 0:
            logging.info("   INFO: Waiting for system.")
            time.sleep(1)
        time.sleep(1)

        # Test if eligibility confirmation button is available
        if len(self.driver.find_elements_by_xpath(self.eligible_button_xpath)) == 0:
            return None

        # Approve eligibility
        logging.info("   ACTION:  confirmation eligibility.")
        self.driver.find_elements_by_xpath(self.eligible_button_xpath)[0].click()
        time.sleep(1)

        # Enter age into input field
        # Backspace is necessary if working in tabbed mode and site is not refreshed
        logging.info("   ACTION: Entering age.")
        self.driver.find_element_by_xpath(self.input_age_field_xpath).send_keys(
            Keys.BACKSPACE + Keys.BACKSPACE + Keys.BACKSPACE
        )
        self.driver.find_element_by_xpath(self.input_age_field_xpath).send_keys(
            str(self.personal_information["age"])
        )
        time.sleep(1)

        # Run final check for appointment
        logging.info("   ACTION: Running final availability check.")
        self.driver.find_elements_by_xpath(self.perform_check_button_xpath)[0].click()

        # Enter personal information
        logging.info("   ACTION: Entering personal information.")
        self.driver.find_element_by_xpath(self.input_email_field_xpath).send_keys(
            self.personal_information["email"]
        )
        self.driver.find_element_by_xpath(self.input_phone_field_xpath).send_keys(
            self.personal_information["phone"]
        )

        # Final submission to receive code
        time.sleep(1)
        self.driver.find_elements_by_xpath(self.final_submit_xpath)[0].click()
        logging.info("   Great SUCCESS. Code has been requested")

        return self._get_result(url)
