import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import allure
import pytest
from App.CreateDriver import driver
import uuid
from App.ConfigStarted import ConfiguratorStarted  # Import the ConfiguratorStarted class

# Generate a consistent UUID for the test using the test name
def generate_test_uuid(test_name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, test_name))

class BFV2Test:
    def __init__(self, driver, urls, test_link=None):
        self.driver = driver
        self.urls = urls
        self.test_link = test_link

    @allure.feature("BFV2 Test Suite")
    @allure.story("Run BFV2 Test")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id(generate_test_uuid("run_bfv2_test"))  # Assign a consistent UUID to the main test
    def run(self):
        """Executes the BFV2 test."""
        try:
            # Execute the main logic of the BFV2 test
            self.perform_bfv2_test()

            # If there is a test link, navigate to Salesforce
            if self.test_link:
                self.navigate_to_salesforce()

        except Exception as e:
            logging.error(f"❌ Error during the BFV2 test: {e}")
            allure.attach(f"Error: {e}", name="Test Error", attachment_type=allure.attachment_type.TEXT)

    @allure.step("Perform BFV2 Test Logic")
    @allure.id(generate_test_uuid("perform_bfv2_test"))  # Consistent UUID for this step
    def perform_bfv2_test(self):
        """Performs the main logic of the BFV2 test."""
        # Create an instance of ConfiguratorStarted
        configurator = ConfiguratorStarted(self.driver)
            
        # Navigate to the product page
        with allure.step(f"🌍 Navigating to: {self.urls['PRODUCT_PAGE']}"):
            self.driver.get(self.urls['PRODUCT_PAGE'])
            logging.info(f"🌍 Navigating to: {self.urls['PRODUCT_PAGE']}")
            time.sleep(3)

        # Navigate to the configurator
        with allure.step(f"🌍 Navigating to: {self.urls['CONFIGURATOR']}"):
            self.driver.get(self.urls['CONFIGURATOR'])
            logging.info(f"🌍 Navigating to: {self.urls['CONFIGURATOR']}")
            time.sleep(4)

        # Call the perform_configurator_actions function from ConfiguratorStarted
        with allure.step("✅ Performing configuration actions"):
            try:
                configurator.perform_configurator_actions()
                logging.info("✅ Successfully performed configuration actions.")
            except Exception as e:
                logging.error(f"❌ Error performing configuration actions: {e}")
                allure.attach(f"Error: {e}", name="Configuration Actions Error", attachment_type=allure.attachment_type.TEXT)
                raise  # Re-raise the exception to handle it at a higher level

        # Navigate back to the home page
        with allure.step(f"🌍 Navigating back to: {self.urls['HOME_PAGE']}"):
            self.driver.get(self.urls['HOME_PAGE'])
            logging.info(f"🌍 Navigating back to: {self.urls['HOME_PAGE']}")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

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