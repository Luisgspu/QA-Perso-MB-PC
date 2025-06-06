import logging
import allure
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

class ImageVerifier:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def verify_image(self, selector: str, expected_path: str, test_name: str = None, timeout: int = 6) -> bool:
        """
        Verifies if an image with the expected `src` is present among all images matching the selector.
        """
        try:
            # Wait for at least one image to be present
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            images = self.driver.find_elements(By.CSS_SELECTOR, selector)
            img_count = len(images)
            logging.info(f"Found {img_count} <img> elements inside {selector}.")

            srcs = []
            found_match = False
            for i, img in enumerate(images):
                src = img.get_attribute("src")
                srcs.append(src)
                logging.info(f"Image {i+1} src: {src}")
                if src and expected_path in src:
                    found_match = True

            logging.info("All found image srcs:\n" + "\n".join([str(s) for s in srcs]))
            # Attach all found image srcs to Allure
            allure.attach(
                "\n".join([str(s) for s in srcs]),
                name="All Found Image Sources",
                attachment_type=allure.attachment_type.TEXT
            )
            if found_match:
                # Find all matching srcs
                matching_srcs = [src for src in srcs if src and expected_path in src]
                # Attach all matching image srcs to Allure
                allure.attach(
                    "\n".join([str(s) for s in matching_srcs]),
                    name="Matching Image Sources",
                    attachment_type=allure.attachment_type.TEXT
                )
                with allure.step(f"✅ Personalized image with expected src '{expected_path}' was applied correctly."):
                    logging.info(f"✅ Personalized image with expected src '{expected_path}' was applied correctly.")
                    return True
            else:
                with allure.step(f"❌ Image not found in the specified selector. Expected src: {expected_path}"):
                    logging.warning(f"❌ Image not found in the specified selector. Expected src: {expected_path}")
                    message = f"❌ Test '{test_name}' failed due to image verification error."
                    pytest.fail(message)
                    return False
        except Exception as e:
            message = f"❌ Test '{test_name}' failed due to image verification error: {e}" if test_name else f"❌ Image verification error: {e}"
            logging.error(message)
            pytest.fail(message)
            return False