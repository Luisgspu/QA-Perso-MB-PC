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

class LSeenSRPTest:
    def __init__(self, driver, urls, test_link=None):
        self.driver = driver
        self.urls = urls
        self.test_link = test_link
        self.retries = 0
        self.max_retries = 5  # Maximum number of retries

    @allure.feature("Last Seen SRP")
    @allure.story("Run Last Seen SRP Test")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.id(generate_test_uuid("run_LSeenSRP_test"))  # Assign a consistent UUID to the main test
    def run(self):
        test_success = False  # Flag to indicate if the test was successful
        
        while self.retries < self.max_retries:

            # Try navigating and performing the Last Seen SRP test logic
            try:
                self.perform_LSSRP_test()
                # If you have a test link, navigate to Salesforce URL
                if self.test_link:
                    self.navigate_to_salesforce()

                test_success = True
                break  # Break the loop if the test is successful
            except Exception as e:
                logging.error(f"❌ Error during Last Seen SRP test: {e}")
                self.retries += 1
                continue

        if not test_success:
            logging.error(f"❌ Last Seen SRP Test failed after {self.max_retries} attempts.")
    
    def expand_shadow_element(self, element):
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root        

    @allure.step("Perform Last Seen SRP Logic")
    @allure.id(generate_test_uuid("perform_LSSRP_test"))  # UUID consistent for this step
    def perform_LSSRP_test(self):
        """Perform the main Last Seen SRP test logic."""        
        try:
            # Navigate to ONLINE STORE
            with allure.step(f"🌍 Navigated to: {self.urls['ONLINE_SHOP']}"):
                self.driver.get(self.urls['ONLINE_SHOP'])
                element = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "img.wbx-vehicle-tile__image-img"))
        )
            logging.info(f"🌍 Navigated to: {self.urls['ONLINE_SHOP']}")
            time.sleep(4)
                        
            # Navigate back to HOME_PAGE
            with allure.step(f"🌍 Navigated back to: {self.urls['HOME_PAGE']}"):
                self.driver.get(self.urls['HOME_PAGE'])
                logging.info(f"🌍 Navigated back to: {self.urls['HOME_PAGE']}")
                WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        except Exception as e:
            logging.error(f"❌ Error during Last Seen SRP: {e}")
                        

    @allure.step("Navigate to Salesforce URL")
    @allure.id(generate_test_uuid("navigate_to_salesforce"))  # UUID consistent for this step
    def navigate_to_salesforce(self):
        """Navigate to the Salesforce URL if test_link is provided."""
        salesforce_url = self.urls['HOME_PAGE'] + self.test_link
        self.driver.get(salesforce_url)
        logging.info(f"🌍 Navigated to Salesforce URL: {salesforce_url}")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))