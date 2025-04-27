import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from App.ConfigCompleted import ConfiguratorCompleted

class PersonalizedCTA4Test:
    def __init__(self, driver, urls, test_link=None):
        self.driver = driver
        self.urls = urls
        self.test_link = test_link
        self.retries = 0
        self.max_retries = 5  # Maximum number of retries

    def run(self):
        test_success = False  # Flag to indicate if the test was successful
        
        while self.retries < self.max_retries:

            # Try navigating and performing the PersonalizedCTA4 test logic
            try:
                self.perform_PersonalizedCTA4_test()

                # If you have a test link, navigate to Salesforce URL
                if self.test_link:
                    self.navigate_to_salesforce()

                test_success = True
                break  # Break the loop if the test is successful
            except Exception as e:
                logging.error(f"❌ Error during Personalized CTA PDP + OWCC test: {e}")
                self.retries += 1
                continue

        if not test_success:
            logging.error(f"❌ Personalized CTA PDP + OWCC Test failed after {self.max_retries} attempts.")

    def perform_PersonalizedCTA4_test(self):
        """Perform the main Personalized CTA PDP + OWCC test logic."""
        # Navigate to the product page
        self.driver.get(self.urls['PRODUCT_PAGE'])
        logging.info(f"🌍 Navigated to: {self.urls['PRODUCT_PAGE']}")
        time.sleep(3)
        
        # Navigate to CONFIGURATOR
        self.driver.get(self.urls['CONFIGURATOR'])
        logging.info(f"🌍 Navigated to: {self.urls['CONFIGURATOR']}")
        time.sleep(4)
        logging.info("🔍 Running Personalized CTA 4 Test...")
        
        # Initialize ConfiguratorCompleted
        configurator = ConfiguratorCompleted(self.driver)
        
        # Call the perform_configurator_actions method
        configurator.perform_configurator_actions()
        
        logging.info("✅ Completed actions in the configurator.")
        
        # Navigate to ONLINE STORE
        self.driver.get(self.urls['ONLINE_SHOP'])
        logging.info(f"🌍 Navigated to: {self.urls['ONLINE_SHOP']}")
        element = WebDriverWait(self.driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "img.wbx-vehicle-tile__image-img"))
        )
        element.click()
        logging.info(f"🌍 Clicked First Search Result")

        logging.info(f"🌍 Waiting for Loading of PDP_Element")
        time.sleep(4)
        
        # Navigate back to the product page
        self.driver.get(self.urls['PRODUCT_PAGE'])
        logging.info(f"🌍 Navigated back to: {self.urls['PRODUCT_PAGE']}")
        WebDriverWait(self.driver, 40).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    def navigate_to_salesforce(self):
        """Navigate to the Salesforce URL if test_link is provided."""
        salesforce_url = self.urls['PRODUCT_PAGE'] + self.test_link
        self.driver.get(salesforce_url)
        logging.info(f"🌍 Navigated to Salesforce URL: {salesforce_url}")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))