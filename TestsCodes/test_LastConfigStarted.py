import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import allure
import uuid
# Generar un UUID consistente para el test usando el nombre del test
def generate_test_uuid(test_name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, test_name))

class LCStartedTest:
    def __init__(self, driver, urls, test_link=None):
        self.driver = driver
        self.urls = urls
        self.test_link = test_link
        self.retries = 0
        self.max_retries = 5  # Maximum number of retries

    @allure.feature("Last Configuration Started Test Suite")
    @allure.story("Run Last Configuration Started Test")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id(generate_test_uuid("run_LCStarted_test"))  # Assign a consistent UUID to the main test
    
    def run(self):
        test_success = False  # Flag to indicate if the test was successful
        
        while self.retries < self.max_retries:

            # Try navigating and performing the Last Configuration Started test logic
            try:
                self.perform_LCStarted_test()

                # If you have a test link, navigate to Salesforce URL
                if self.test_link:
                    self.navigate_to_salesforce()

                test_success = True
                break  # Break the loop if the test is successful
            except Exception as e:
                logging.error(f"❌ Error during Last Configuration Started test: {e}")
                self.retries += 1
                continue

        if not test_success:
            logging.error(f"❌ Last Configuration Started Test failed after {self.max_retries} attempts.")
    
    def expand_shadow_element(self, element):
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root        

    @allure.step("Perform Last Configuration Started Test Logic")
    @allure.id(generate_test_uuid("perform_LCStarted_test"))  # UUID consistent for this step
    def perform_LCStarted_test(self):
        """Perform the main Last Configuration Started test logic."""
       
        # Navigate to CONFIGURATOR
        with allure.step(f"🌍 Navigated to: {self.urls['CONFIGURATOR']}"):
            self.driver.get(self.urls['CONFIGURATOR'])
            logging.info(f"🌍 Navigated to: {self.urls['CONFIGURATOR']}")
            time.sleep(4)

        # Execute actions in CONFIGURATOR
        with allure.step(f"✅ Executed actions in configurator"):
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owcc-car-configurator')
            shadow_root = self.expand_shadow_element(shadow_host)
            main_frame = shadow_root.find_element(By.CSS_SELECTOR, '#cc-app-container-main > div.cc-app-container__main-frame.cc-grid-container > div.cc-app-container__navigation.ng-star-inserted > cc-navigation > nav > div > ul > li:nth-child(3) > ccwb-text > a')
                    
        # Hover over the main frame
        actions = ActionChains(self.driver)
        actions.move_to_element(main_frame).perform()
        logging.info('✅ Hovered over Navigation main frame')
                    
        # Click on the main frame
        main_frame.click()
        logging.info('✅ Clicked on Navigation main frame')
        time.sleep(5)
        
        # Navigate back to the home page  
        with allure.step(f"🌍 Navigated back to: {self.urls['HOME_PAGE']}"):
            self.driver.get(self.urls['HOME_PAGE'])
            logging.info(f"🌍 Navigated back to: {self.urls['HOME_PAGE']}")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
    @allure.step("Navigate to Salesforce URL")
    @allure.id(generate_test_uuid("navigate_to_salesforce"))  # UUID consistent for this step
    def navigate_to_salesforce(self):
        """Navigate to the Salesforce URL if test_link is provided."""
        salesforce_url = self.urls['HOME_PAGE'] + self.test_link
        self.driver.get(salesforce_url)
        logging.info(f"🌍 Navigated to Salesforce URL: {salesforce_url}")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))