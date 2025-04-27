import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from App.CTAVerifier import CTAVerifier

class CTAHandler:
    def __init__(self, driver):
        """
        Initialize the ShadowHostHandler with a Selenium WebDriver instance.
        """
        self.driver = driver

    def expand_shadow_element(self, element):
        """
        Expands a shadow root element.
        """
        return self.driver.execute_script('return arguments[0].shadowRoot', element)

    def locate_shadow_host(self, shadow_host_selector, fallback_parent_selector=None):
        """
        Locate the shadow host element and expand its shadow root.
        If the shadow host is not found, fallback to using the CTAVerifier and a fallback parent element.
        """
        try:
            # Wait for the shadow host to be present
            shadow_host = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, shadow_host_selector))
            )
            shadow_root = self.expand_shadow_element(shadow_host)
            logging.info("✅ Shadow host located and shadow root expanded.")
            return shadow_root
        except Exception as e:
            logging.error(f"❌ Shadow host not found: {e}")
            if fallback_parent_selector:
                logging.info("🔄 Falling back to CTAVerifier and fallback parent element.")
                try:
                    # Use the fallback parent element
                    fallback_parent = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, fallback_parent_selector))
                    )
                    logging.info("✅ Fallback parent element located.")
                    return fallback_parent
                except Exception as fallback_error:
                    logging.error(f"❌ Fallback parent element not found: {fallback_error}")
                    return None

    def locate_parent_element(self, shadow_root, parent_selector):
        """
        Locate the parent element within the shadow DOM.
        """
        try:
            parent_element = shadow_root.find_element(By.CSS_SELECTOR, parent_selector)
            logging.info("✅ Parent element located.")
            return parent_element
        except Exception as e:
            logging.error(f"❌ Parent element not found: {e}")
            return None

    def locate_cta(self, parent_element, cta_selector, expected_href, cta_type="Primary"):
        """
        Locate a CTA element within the parent element and verify its href.
        """
        try:
            cta_element = parent_element.find_element(By.CSS_SELECTOR, cta_selector)
            logging.info(f"✅ {cta_type} CTA element located.")

            # Verify the href attribute
            href_value = cta_element.get_attribute("href")
            if expected_href in href_value:
                logging.info(f"✅ The href attribute includes '{expected_href}': {href_value}")
            else:
                logging.warning(f"⚠️ The href attribute does not include '{expected_href}': {href_value}")

            return cta_element
        except Exception as e:
            logging.error(f"❌ {cta_type} CTA element not found: {e}")
            return None

    def verify_ctas(self, shadow_host_selector, parent_selector, fallback_parent_selector, primary_cta_selector, secondary_cta_selector, expected_primary_href, expected_secondary_href):
        try:
            # Wait for the shadow host to be present and visible
            shadow_host = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, shadow_host_selector))
            )
            logging.info("✅ Shadow host located.")
        except Exception as e:
            logging.error(f"❌ Shadow host not found: {e}")
            logging.info("🔄 Falling back to CTAVerifier.")
        
            # Call the CTAVerifier function
            try:
                verifier = CTAVerifier(self.driver)
                fallback_result = verifier.verify_ctas(
                    fallback_parent_selector,
                    primary_cta_selector,
                    secondary_cta_selector,
                    expected_primary_href,
                    expected_secondary_href
                )
                if fallback_result:
                    logging.info("✅ CTAVerifier successfully verified CTAs.")
                    return True
                else:
                    logging.error("❌ CTAVerifier failed to verify CTAs.")
                    return False
            except Exception as verifier_error:
                logging.error(f"❌ Error while using CTAVerifier: {verifier_error}")
                return False
            

        try:
            # Expand the shadow root
            shadow_root = self.driver.execute_script("return arguments[0].shadowRoot", shadow_host)
            logging.info("✅ Shadow root expanded.")
        except Exception as e:
            logging.error(f"❌ Failed to expand shadow root: {e}")
            return False

        try:
            # Locate the parent element
            parent_element = shadow_root.find_element(By.CSS_SELECTOR, parent_selector)
            logging.info("✅ Parent element located.")
        except Exception as e:
            logging.error(f"❌ Parent element not found: {e}")
            return False

        try:
            # Locate and verify the primary CTA
            primary_cta = parent_element.find_element(By.CSS_SELECTOR, primary_cta_selector)
            logging.info("✅ Primary CTA located.")
            primary_href = primary_cta.get_attribute("href")
            logging.info(f"Primary CTA href: {primary_href}")

            # Verify the primary CTA href
            if expected_primary_href in primary_href:
                logging.info(f"✅ Primary CTA href matches expected value: {expected_primary_href}")
            else:
                logging.warning(f"⚠️ Primary CTA href does not match expected value. Expected: {expected_primary_href}, Found: {primary_href}")
        except Exception as e:
            logging.error(f"❌ Primary CTA not found: {e}")
            return False

        try:
            # Locate and verify the secondary CTA
            secondary_cta = parent_element.find_element(By.CSS_SELECTOR, secondary_cta_selector)
            logging.info("✅ Secondary CTA located.")
            secondary_href = secondary_cta.get_attribute("href")
            logging.info(f"Secondary CTA href: {secondary_href}")

            # Verify the secondary CTA href
            if expected_secondary_href in secondary_href:
                logging.info(f"✅ Secondary CTA href matches expected value: {expected_secondary_href}")
            else:
                logging.warning(f"⚠️ Secondary CTA href does not match expected value. Expected: {expected_secondary_href}, Found: {secondary_href}")
        except Exception as e:
            logging.error(f"❌ Secondary CTA not found: {e}")
            return False

        return True