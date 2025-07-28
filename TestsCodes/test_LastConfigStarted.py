import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import allure
import uuid
from App.ConfigStarted import ConfiguratorStarted  # Import the ConfiguratorStarted class

# Generate a consistent UUID for the test using the test name
def generate_test_uuid(test_name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, test_name))

class LCStartedTest:
    def __init__(self, driver, urls, test_link=None):
        self.driver = driver
        self.urls = urls
        self.test_link = test_link

    @allure.feature("Last Configuration Started Test Suite")
    @allure.story("Run Last Configuration Started Test")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id(generate_test_uuid("run_LCStarted_test"))  # Assign a consistent UUID to the main test
    def run(self):
        """Executes the Last Configuration Started test."""
        try:
           
            # Execute the main logic of the Last Configuration Started test
            self.perform_LCStarted_test()
                 
            # If there is a test link, navigate to Salesforce
            if self.test_link:
                self.navigate_to_salesforce()
        except Exception as e:
            logging.error(f"❌ Error during the BFV2 test: {e}")
            allure.attach(f"Error: {e}", name="Test Error", attachment_type=allure.attachment_type.TEXT)        
    
    @allure.step("Perform Last Configuration Started Test Logic")
    @allure.id(generate_test_uuid("LCCompleted_test"))  # UUID consistente para este paso
    def perform_LCStarted_test(self):
        # Create an instance of ConfiguratorStarted
        configurator = ConfiguratorStarted(self.driver)
            
        """Perform the main Last Configuration Started test logic."""
        # Create an instance of ConfiguratorStarted
        configurator = ConfiguratorStarted(self.driver)        
        try:
             # Navigate to the configurator and perform actions
            with allure.step(f"🌍 Navigated to: {self.urls['CONFIGURATOR']}"):
                self.driver.get(self.urls['CONFIGURATOR'])
                logging.info(f"🌍 Navigating to the configurator: {self.urls['CONFIGURATOR']}")
                WebDriverWait(self.driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                time.sleep(4)

            # Call the perform_configurator_actions function from ConfiguratorStarted
            with allure.step("✅ Performing configuration actions"):
                try:
                    configurator.perform_configurator_actions()
                    logging.info("✅ Successfully performed configuration actions.")
                    time.sleep(4)
                except Exception as e:
                    logging.error(f"❌ Error performing configuration actions: {e}")
                    allure.attach(f"Error: {e}", name="Configuration Actions Error", attachment_type=allure.attachment_type.TEXT)
                    raise  # Re-raise the exception to handle it at a higher level
                
            # Navigate back to the home page
            with allure.step(f"🌍 Navigating back to: {self.urls['HOME_PAGE']}"):
                self.driver.get(self.urls['HOME_PAGE'])
                logging.info(f"🌍 Navigating back to: {self.urls['HOME_PAGE']}")
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(3)
                        
        except Exception as e:
            logging.error(f"❌ Error in configurator: {e}")        

    @allure.step("Navigate to Salesforce URL")
    @allure.id(generate_test_uuid("navigate_to_salesforce"))  # Consistent UUID for this step
    def navigate_to_salesforce(self):
        """Navigates to the Salesforce link if provided."""
        try:
            salesforce_url = self.urls['HOME_PAGE'] + self.test_link
            self.driver.get(salesforce_url)
            logging.info(f"🌍 Navigating to Salesforce URL: {salesforce_url}")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except Exception as e:
            logging.error(f"❌ Error navigating to Salesforce URL: {e}")
            allure.attach(f"Error: {e}", name="Salesforce Navigation Error", attachment_type=allure.attachment_type.TEXT)