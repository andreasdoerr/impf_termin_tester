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

    def __init__(self, binary_location, chrome_driver, use_tabs=False):
        # Path to chrome executable and chrome driver executable
        self.binary_location = binary_location
        self.chrome_driver = chrome_driver

        self.tab_list = []
        self.use_tabs = use_tabs
        
        # x-path for elements on the website
        self.cookie_xpath = "/html/body/app-root/div/div/div/div[2]/div[2]/div/div[2]/a"
        self.button_xpath = "/html/body/app-root/div/app-page-its-search/div/div/div[2]/div/div/div[5]/div/div[1]/div[2]/div[2]/button"
        self.cancel_xpath = "/html/body/app-root/div/app-page-its-search/app-its-search-slots-modal/div/div/div/div[2]/div/div/form/div[2]/button[2]"
        self.button_choose_xpath = "/html/body/app-root/div/app-page-its-search/app-its-search-slots-modal/div/div/div/div[2]/div/div/form/div[2]/button[1]"
        self.select_bw_xpath = "/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[3]/app-corona-vaccination-center/div[1]/label/span[2]/span[1]/span"
        self.select_center_xpath = "/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[3]/app-corona-vaccination-center/div[2]/label/span[2]/span[1]/span/span[1]"
        self.select_center_xpath = "/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[3]/app-corona-vaccination-center/div[2]/label/span[2]/span[1]/span"
        self.goto_center_xpath = "/html/body/app-root/div/app-page-its-center/div/div[2]/div/div/div/div/form/div[4]/button"

    def initialize(self):
        opts = Options()
        opts.binary_location = self.binary_location
        self.driver = webdriver.Chrome(options=opts, executable_path=self.chrome_driver)
        self.driver.set_window_size(400, 700)

    def _get_result(self, url):
        # Take screenshot
        screenshot = self.driver.get_screenshot_as_base64()

        # Current time
        current_time = datetime.now()

        source = self.driver.page_source

        # Return result object
        result = self.Result(
            source=source, screenshot=screenshot, time=current_time, url=url
        )
        return result



    def check_cookies(self, url):
        # Accept cookies if available
        try:
            cookie_button = self.driver.find_element_by_xpath(self.cookie_xpath)
            cookie_button.click()
            logging.info("   ACTION: Acknowledge cookies.")
            time.sleep(3)
            logging.info("   ACTION: Reload website")
            self.driver.get(url)
            logging.info("           Done")
            time.sleep(2)
        except NoSuchElementException:
            pass



    def get_url(self, url):
        if self.use_tabs == True:
            has_opened = False
            for tab in self.tab_list:
                if tab.url == url:
                    has_opened = True
                    self.driver.switch_to.window(tab.window_handle)
                    break
            
            if not has_opened:
                if len(self.tab_list) > 0:
                    script_str =  '''window.open(\"'''+ url + '''\" ,\"_blank\");'''
                    self.driver.execute_script(script_str)
                self.tab_list.append(self.Tab(url=url, window_handle=self.driver.window_handles[-1]))
                
            reload_site = True    
            # Open website
            if self.driver.page_source.find("Warteraum") > 0:
                reload_site = False
            # if self.driver.page_source.find("Terminsuche") >= 0 and \
            #         self.driver.page_source.find("Derzeit stehen leider keine Termine zur Verfügung") < 0:
            #     reload_site = False    
            choose_button = self.driver.find_elements_by_xpath(self.button_choose_xpath)
            if len(choose_button) > 0 and  choose_button[0].is_enabled():      
                reload_site = False
            if self.driver.page_source.find("00min 00s"):
                reload_site = True
            
            if reload_site == True:
                logging.info("   INFO: Loading URL.")
                self.driver.get(url)
            else:
                logging.info("   INFO: Waiting for system.")

                
            
        else:
            self.driver.get(url)
        
        #Approve Cookies
        time.sleep(2)
        self.check_cookies(url)


    ## Get URL For Appointment
    def check_url(self, url):
        # Open website
        self.get_url(url)
        time.sleep(5)

        # Catch redirect to landing page
        if len (self.driver.find_elements_by_xpath(self.select_bw_xpath)) > 0:
            logging.info("   INFO: Redirect from landing page.")
            self.driver.find_elements_by_xpath(self.select_bw_xpath)[0].click()
            self.driver.find_elements_by_xpath(self.select_bw_xpath)[0].send_keys(Keys.ENTER)
            self.driver.find_elements_by_xpath(self.select_center_xpath)[0].click()
            self.driver.find_elements_by_xpath(self.select_center_xpath)[0].send_keys(Keys.ENTER)
            self.driver.find_elements_by_xpath(self.goto_center_xpath)[0].click() 
            self.get_url(url)
            time.sleep(5)
      

          
        choose_button = self.driver.find_elements_by_xpath(self.button_choose_xpath)
        if len(choose_button) > 0 and  choose_button[0].is_enabled():      
            return self._get_result(url)
        
        # Click appointment button  
        submit_button = self.driver.find_elements_by_xpath(self.button_xpath)
        if len(submit_button) != 1:
            logging.info(f"   WARNING: Found {len(submit_button)} buttons.")
            return None
        else:
            logging.info("   ACTION: Click button.")
            submit_button[0].click()
            time.sleep(5)
        
        while self.driver.page_source.find("Termine werden gesucht") >= 0:
            logging.info("   Info: Waiting for system to find appointment.")
            time.sleep(1)
            
        # Check if no appointment text visible
        source = self.driver.page_source
        if source.find("Derzeit stehen leider keine Termine zur Verfügung") >= 0:
            # self.driver.find_element_by_xpath(self.cancel_xpath).click()
            return None
        if source.find("Virtueller Warteraum des Impfterminservice") > -1:
            return None
        if source.find("Wir aktualisieren zurzeit das System. Bitte probieren Sie es in einigen Minuten erneut.") > -1:
            return None    
            
        return self._get_result(url)

    def get_dummy_result(self):
        
        # Open Google as dummy website
        url = "http://www.google.com"
        
        # Open website
        self.driver.get(url)
        time.sleep(3)
        
        # Get page source
        source = self.driver.page_source
        
        # Take screenshot
        screenshot = self.driver.get_screenshot_as_base64()


class Browser_Get_Code(Browser):
    
    def __init__(self, binary_location, chrome_driver, use_tabs=False, personal_information=dict()):
        super().__init__(binary_location, chrome_driver, use_tabs)

        self.check_button_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[2]/div/div/label[2]/span"
        self.eligible_button_xpath ="/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/app-corona-vaccination-no/form/div[1]/div/div/label[1]/span"
        self.input_age_field_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/app-corona-vaccination-no/form/div[3]/div/div/input"
        self.perform_check_button_xpath = "/html/body/app-root/div/app-page-its-login/div/div/div[2]/app-its-login-user/div/div/app-corona-vaccination/div[3]/div/div/div/div[2]/div/app-corona-vaccination-no/form/div[4]/button"
        self.input_email_field_xpath = "/html/body/app-root/div/app-page-its-check-result/div/div/div[2]/div/div/div/div/app-its-check-success/div/form/div[1]/label/input"
        self.input_phone_field_xpath = "/html/body/app-root/div/app-page-its-check-result/div/div/div[2]/div/div/div/div/app-its-check-success/div/form/div[2]/label/div/input"
        self.final_submit_xpath = "/html/body/app-root/div/app-page-its-check-result/div/div/div[2]/div/div/div/div/app-its-check-success/div/form/div[3]/button"
        
        
        self.personal_information = personal_information
        
    def get_url(self, url):
        if self.use_tabs == True:
            has_opened = False
            for tab in self.tab_list:
                if tab.url == url:
                    has_opened = True
                    self.driver.switch_to.window(tab.window_handle)
                    break
            
            if not has_opened:
                if len(self.tab_list) > 0:
                    script_str =  '''window.open(\"'''+ url + '''\" ,\"_blank\");'''
                    self.driver.execute_script(script_str)
                else:
                    # Open website
                    self.driver.get(url)

                
                self.tab_list.append(self.Tab(url=url, window_handle=self.driver.window_handles[-1]))
        else:
            self.driver.get(url)
        
        #Approve Cookies
        time.sleep(2)
        self.check_cookies(url)

    def check_url(self, url):
        if self.driver.page_source.find("SMS Verifizierung") >= 0:
            return self._get_result(url)

        self.get_url(url)
        
        # Click first check for eligibility button
        check_button = self.driver.find_elements_by_xpath(self.check_button_xpath)
        
        if len(check_button) != 1:
            logging.info(f"   WARNING: Found {len(submit_button)} buttons.")
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
        
        #Test if eligibility confirmation button is available
        if len(self.driver.find_elements_by_xpath(self.eligible_button_xpath)) == 0: 
            return None
        
        
        #Approve eligibility
        logging.info("   ACTION:  confirmation eligibility.")
        self.driver.find_elements_by_xpath(self.eligible_button_xpath)[0].click()
        time.sleep(1)
        
        # Enter age into input field
        # Backspace is necessary if working in tabbed mode and site is not refreshed
        logging.info("   ACTION: Entering age.")
        self.driver.find_element_by_xpath(self.input_age_field_xpath).send_keys(Keys.BACKSPACE+Keys.BACKSPACE+Keys.BACKSPACE)
        self.driver.find_element_by_xpath(self.input_age_field_xpath).send_keys(str(self.personal_information['age']))
        time.sleep(1)

        # Run final check for appointment
        logging.info("   ACTION: Running final availability check.")
        self.driver.find_elements_by_xpath(self.perform_check_button_xpath)[0].click()

        # Enter personal information
        logging.info("   ACTION: Entering personal information.")
        self.driver.find_element_by_xpath(self.input_email_field_xpath).send_keys(self.personal_information['email'])
        self.driver.find_element_by_xpath(self.input_phone_field_xpath).send_keys(self.personal_information['phone'])

        # Final submission to receive code
        time.sleep(1)
        self.driver.find_elements_by_xpath(self.final_submit_xpath)[0].click()
        logging.info("   Great SUCCESS. Code has been requested")


        return self._get_result(url)
    
=======
        # Return result object
        result = self.Result(
            source=source, screenshot=screenshot, time=current_time, url=url
        )
        
        return result

>>>>>>> master
