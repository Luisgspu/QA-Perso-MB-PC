import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CTAVerifier:
    def __init__(self, driver):
        """Initialize the CTAVerifier with a Selenium WebDriver instance."""
        self.driver = driver

    def handle_cookies(self):
        """Handles the cookie banner if present."""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "cmm-cookie-banner"))
            )
            logging.info("✅ Cookie banner detected.")
            self.driver.execute_script("""
                document.querySelector("cmm-cookie-banner").shadowRoot.querySelector("wb7-button.button--accept-all").click();
            """)
            logging.info("✅ Clicked on the cookie acceptance button.")
        except Exception as ex:
            logging.warning(f"⚠️ Could not click cookie banner: {ex}")

    def verify_ctas(self, parent_selector, primary_cta_selector, secondary_cta_selector, expected_primary_href, expected_secondary_href):
        """
        Verifies the primary and secondary CTAs on the page.

        Returns:
            bool: True if both CTAs contain the expected hrefs, False otherwise.
        """
        try:
            # Locate the parent element
            parent_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, parent_selector))
            )
            logging.info("✅ Parent element located.")

            primary_verified = False
            secondary_verified = False

            # Verify the primary CTA
            try:
                primary_cta = parent_element.find_element(By.CSS_SELECTOR, primary_cta_selector)
                logging.info("✅ Primary CTA located.")
                if primary_cta.is_displayed():
                    logging.info("✅ Primary CTA is visible.")
                    primary_href = primary_cta.get_attribute("href")
                    logging.info(f"Primary CTA href: {primary_href}")

                    # Verify the primary CTA href
                    if expected_primary_href in primary_href:
                        logging.info(f"✅ Primary CTA href contains the expected value: {expected_primary_href}")
                        primary_verified = True
                    else:
                        logging.warning(f"⚠️ Primary CTA href does not contain the expected value. Expected to contain: {expected_primary_href}, Found: {primary_href}")
                else:
                    logging.warning("⚠️ Primary CTA is not visible.")
            except Exception as e:
                logging.error(f"❌ Primary CTA not found. Error: {e}")

            # Verify the secondary CTA
            try:
                secondary_cta = parent_element.find_element(By.CSS_SELECTOR, secondary_cta_selector)
                logging.info("✅ Secondary CTA located.")
                if secondary_cta.is_displayed():
                    logging.info("✅ Secondary CTA is visible.")
                    secondary_href = secondary_cta.get_attribute("href")
                    logging.info(f"Secondary CTA href: {secondary_href}")

                    # Verify the secondary CTA href
                    if expected_secondary_href in secondary_href:
                        logging.info(f"✅ Secondary CTA href contains the expected value: {expected_secondary_href}")
                        secondary_verified = True
                    else:
                        logging.warning(f"⚠️ Secondary CTA href does not contain the expected value. Expected to contain: {expected_secondary_href}, Found: {secondary_href}")
                else:
                    logging.warning("⚠️ Secondary CTA is not visible.")
            except Exception as e:
                logging.error(f"❌ Secondary CTA not found. Error: {e}")

            # Return True if both CTAs are verified
            return primary_verified and secondary_verified

        except Exception as e:
            logging.error(f"❌ Parent element not found: {parent_selector}. Error: {e}")
        return False