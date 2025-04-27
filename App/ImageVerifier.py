import time
import logging
from selenium.webdriver.common.by import By

class ImageVerifier:
    def __init__(self, driver):
        """Initializes the ImageVerifier with a WebDriver instance."""
        self.driver = driver

    def verify_image(self, selector, expected_path):
        """Verifies if an image with the expected `src` is present."""
        time.sleep(2)  # Wait for the images to load
        try:
            images = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return any(expected_path in (img.get_attribute("src") or "") for img in images)
        except Exception as e:
            logging.error(f"❌ Could not verify personalized image: {e}")
            return False