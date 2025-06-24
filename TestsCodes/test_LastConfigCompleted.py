import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import allure
import uuid
from App.ConfigCompleted import ConfiguratorCompleted  # Import the ConfiguratorCompleted class

# Generar un UUID consistente para el test usando el nombre del test
def generate_test_uuid(test_name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, test_name))


class LCCompletedTest:
    def __init__(self, driver, urls, test_link=None):
        self.driver = driver
        self.urls = urls
        self.test_link = test_link
        self.retries = 0
        self.max_retries = 5  # Maximum number of retries

    @allure.feature("Last Configuration Completed Test Suite")
    @allure.story("Run Last Configuration Completed Test")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id(generate_test_uuid("run_LCCompleted_test"))  # Assign a consistent UUID to the main test
    def run(self):
        
        try:
            self.perform_LCCompleted_test()

            # If you have a test link, navigate to Salesforce URL
            if self.test_link:
                self.navigate_to_salesforce()

 
        except Exception as e:
            logging.error(f"❌ Error during Last Configuration Completed test: {e}")
          

      
    
    def expand_shadow_element(self, element):
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root        

    @allure.step("Perform Last Configuration Completed Logic")
    @allure.id(generate_test_uuid("perform_LCCompleted_test"))  # UUID consistent for this step
    def perform_LCCompleted_test(self):
        """Perform the main Last Configuration Completed test logic."""
        # Create an instance of ConfiguratorCompleted
        configurator = ConfiguratorCompleted(self.driver)        
        
        try:
            # Navigate to CONFIGURATOR
            with allure.step(f"🌍 Navigated to: {self.urls['CONFIGURATOR']}"):
                self.driver.get(self.urls['CONFIGURATOR'])
                logging.info(f"🌍 Navigated to: {self.urls['CONFIGURATOR']}")
                time.sleep(4)

            # Execute actions in CONFIGURATOR
            with allure.step("✅ Performing configuration actions"):
                try:
                    configurator.perform_configurator_actions()
                    logging.info("✅ Successfully performed configuration actions.")
                except Exception as e:
                    logging.error(f"❌ Error performing configuration actions: {e}")
                    allure.attach(f"Error: {e}", name="Configuration Actions Error", attachment_type=allure.attachment_type.TEXT)
                    raise  # Re-raise the exception to handle it at a higher level
        except Exception as e:
            logging.error(f"❌ Error in configurator: {e}")          
        
        # Navigate back to the home page
        with allure.step(f"🌍 Navigated back to: {self.urls['HOME_PAGE']}"):
            self.driver.get(self.urls['HOME_PAGE'])
            logging.info(f"🌍 Navigated back to: {self.urls['HOME_PAGE']}")
            WebDriverWait(self.driver, 25).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(4)

    @allure.step("Navigate to Salesforce URL")
    @allure.id(generate_test_uuid("navigate_to_salesforce"))  # UUID consistent for this step
    def navigate_to_salesforce(self):
        """Navigate to the Salesforce URL if test_link is provided."""
        salesforce_url = self.urls['HOME_PAGE'] + self.test_link
        self.driver.get(salesforce_url)
        logging.info(f"🌍 Navigated to Salesforce URL: {salesforce_url}")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))