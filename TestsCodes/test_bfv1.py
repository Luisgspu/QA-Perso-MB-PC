import logging
import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest
from App.CreateDriver import driver 
import uuid

# Generar un UUID consistente para el test usando el nombre del test
def generate_test_uuid(test_name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, test_name))

class BFV1Test:
    def __init__(self, driver, urls, market_code=None, model_code=None, test_link=None):
        self.driver = driver
        self.urls = urls
        self.market_code = market_code
        self.model_code = model_code
        self.test_link = test_link
        self.retries = 0
        self.max_retries = 5

    @allure.feature("BFV1 Test Suite")
    @allure.story("Run BFV1 Test")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id(generate_test_uuid("run_bfv1_test"))  # Asignar un UUID consistente al test principal
    def run(self):
        """Run the BFV1 test with retry logic."""
        test_success = False

        for attempt in range(self.max_retries):
            try:
                self.perform_bfv1_test()

                if self.test_link:
                    self.navigate_to_salesforce()

                test_success = True
                break
            except Exception as e:
                logging.error(f"❌ Error during BFV1 test: {e}")
                self.retries += 1
                allure.attach(str(e), name="Error Details", attachment_type=allure.attachment_type.TEXT)

        if not test_success:
            raise Exception(f"❌ BFV1 Test failed after {self.max_retries} attempts.")

    @allure.step("Perform BFV1 Test Logic")
    @allure.id(generate_test_uuid("perform_bfv1_test"))  # UUID consistente para este paso
    def perform_bfv1_test(self):
        """Perform the main BFV1 test logic."""
        # Navigate to the product page
        with allure.step(f"🌍 Navigating to: {self.urls['PRODUCT_PAGE']}"):
            self.driver.get(self.urls['PRODUCT_PAGE'])
            logging.info(f"🌍 Navigated to: {self.urls['PRODUCT_PAGE']}")
            time.sleep(3)

        # Navigate back to the home page
        with allure.step(f"🌍 Navigating back to: {self.urls['HOME_PAGE']}"):
            self.driver.get(self.urls['HOME_PAGE'])
            logging.info(f"🌍 Navigated back to: {self.urls['HOME_PAGE']}")
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    @allure.step("Navigate to Salesforce URL")
    @allure.id(generate_test_uuid("navigate_to_salesforce"))  # UUID consistente para este paso
    def navigate_to_salesforce(self):
        """Navigate to the Salesforce URL if test_link is provided."""
        salesforce_url = self.urls['HOME_PAGE'] + self.test_link
        self.driver.get(salesforce_url)
        logging.info(f"🌍 Navigated to Salesforce URL: {salesforce_url}")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))


