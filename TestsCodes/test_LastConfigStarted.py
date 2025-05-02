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
            # Create an instance of ConfiguratorStarted
            configurator = ConfiguratorStarted(self.driver)

            # Navigate to the configurator and perform actions
            with allure.step(f"🌍 Navigated to: {self.urls['CONFIGURATOR']}"):
                self.driver.get(self.urls['CONFIGURATOR'])
                logging.info(f"🌍 Navigating to the configurator: {self.urls['CONFIGURATOR']}")
                WebDriverWait(self.driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                time.sleep(3)

            with allure.step("✅ Performed configurator actions"):
                # Call the perform_configurator_actions function from ConfiguratorStarted
                try:
                    configurator.perform_configurator_actions()
                    logging.info("✅ Successfully performed actions in the configurator.")
                except Exception as e:
                    logging.error(f"❌ Error performing actions in the configurator: {e}")
                    allure.attach(f"Error: {e}", name="Configurator Actions Error", attachment_type=allure.attachment_type.TEXT)
                    raise

            # Navigate back to the home page
            with allure.step(f"🌍 Navigating back to: {self.urls['HOME_PAGE']}"):
                self.driver.get(self.urls['HOME_PAGE'])
                logging.info(f"🌍 Navigating back to: {self.urls['HOME_PAGE']}")
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # If there is a test link, navigate to Salesforce
            if self.test_link:
                self.navigate_to_salesforce()

        except Exception as e:
            logging.error(f"❌ Error during the Last Configuration Started test: {e}")
            allure.attach(f"Error: {e}", name="Test Error", attachment_type=allure.attachment_type.TEXT)

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