import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
import pytest


class CTAVerifier:
    def __init__(self, driver):
        """Initialize the CTAVerifier with a Selenium WebDriver instance."""
        self.driver = driver


    def verify_ctas(self, parent_selector, primary_cta_selector, expected_href_value):
        """
        Verifies the primary CTA on the page.

        Args:
            parent_selector (str): CSS selector for the parent element.
            primary_cta_selector (str): CSS selector for the primary CTA element.
            expected_href_value (str): Expected href value for the primary CTA.

        Returns:
            bool: True if the primary CTA contains the expected href, False otherwise.
        """
        try:
            # Locate the parent element
            parent_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, parent_selector))
            )
            logging.info("✅ Parent element located.")

            # Verify the primary CTA
            try:
                primary_cta = parent_element.find_element(By.CSS_SELECTOR, primary_cta_selector)
                logging.info("✅ Primary CTA located.")
                if primary_cta.is_displayed():
                    logging.info("✅ Primary CTA is visible.")
                    primary_href = primary_cta.get_attribute("href")
                    logging.info(f"Primary CTA href: {primary_href}")

                    # Verify if the href includes the expected value
                    if expected_href_value in primary_href:
                        with allure.step(f"✅ CTA Verified Succesfully. The href attribute includes the expected value: {expected_href_value}"):
                            allure.attach(primary_href, name="Matching href value found", attachment_type=allure.attachment_type.TEXT)
                            logging.info(f"✅ The href attribute includes the expected value: {expected_href_value}")
                            return True
                    else:
                        with allure.step (f"❌ CTA Verification Failure: The href attribute does not include the expected value: {expected_href_value}"):     
                            message = f"❌ CTA Verification Failure: The href attribute does not include the expected value in the primary PDP CTA."
                            logging.warning(message)
                            allure.attach(primary_href, name="href value found", attachment_type=allure.attachment_type.TEXT)
                            pytest.fail(message)
                else:
                    message = "⚠️ Primary CTA is not visible."
                    logging.warning(message)
                    allure.attach(message, name="CTA Visibility Failure", attachment_type=allure.attachment_type.TEXT)
                    pytest.fail(message)
            except Exception as e:
                message = f"❌ Primary CTA not found. Error: {e}"
                logging.error(message)
                allure.attach(message, name="CTA Not Found Error", attachment_type=allure.attachment_type.TEXT)
                pytest.fail(message)

        except Exception as e:
            message = f"❌ Parent element not found: {parent_selector}. Error: {e}"
            logging.error(message)
            allure.attach(message, name="Parent Element Not Found Error", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(message)