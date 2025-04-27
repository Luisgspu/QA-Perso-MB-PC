import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class PersonalizedCTA1Test:
    def __init__(self, driver, urls, test_link=None):
        self.driver = driver
        self.urls = urls
        self.test_link = test_link
        self.retries = 0
        self.max_retries = 5  # Maximum number of retries

    def run(self):
        test_success = False  # Flag to indicate if the test was successful
        
        while self.retries < self.max_retries:

            # Try navigating and performing the PersonalizedCTA1 test logic
            try:
                self.perform_PersonalizedCTA1_test()

                # If you have a test link, navigate to Salesforce URL
                if self.test_link:
                    self.navigate_to_salesforce()

                test_success = True
                break  # Break the loop if the test is successful
            except Exception as e:
                logging.error(f"❌ Error during Personalized CTA Affinity test: {e}")
                self.retries += 1
                continue

        if not test_success:
            logging.error(f"❌ Personalized CTA Affinity Test failed after {self.max_retries} attempts.")

    def perform_PersonalizedCTA1_test(self):
        """Perform the main Personalized CTA Affinity test logic."""
        # Navigate to the product page
        self.driver.get(self.urls['PRODUCT_PAGE'])
        logging.info(f"🌍 Navigated to: {self.urls['PRODUCT_PAGE']}")
        time.sleep(3)
        
        # Navigate back to the product page
        self.driver.get(self.urls['PRODUCT_PAGE'])
        logging.info(f"🌍 Navigated back to: {self.urls['PRODUCT_PAGE']}")
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    def navigate_to_salesforce(self):
        """Navigate to the Salesforce URL if test_link is provided."""
        salesforce_url = self.urls['PRODUCT_PAGE'] + self.test_link
        self.driver.get(salesforce_url)
        logging.info(f"🌍 Navigated to Salesforce URL: {salesforce_url}")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))