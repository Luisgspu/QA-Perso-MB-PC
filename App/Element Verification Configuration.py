from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import unittest
import logging
import time
import os


class ConfiguratorActionsTest(unittest.TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless') # Uncomment this line to run in headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--enable-webgl")
        #options.add_argument("--maximize")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        options.add_argument("profile-directory=Default")
        #options.add_argument("--start-fullscreen")
        self.driver = webdriver.Chrome(options=options)
        self.driver.fullscreen_window()
        logging.info("✅ Browser opened in headless mode and in full-screen.")

    def tearDown(self):
        self.driver.quit()
        logging.info("✅ Browser closed.")

    def handle_cookies(self):
        """Handles the cookie banner if present."""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "cmm-cookie-banner"))
            )
            time.sleep(2)
            logging.info("✅ Cookie banner detected.")

            self.driver.execute_script("""
                document.querySelector("cmm-cookie-banner").shadowRoot.querySelector("wb7-button.button--accept-all").click();
            """)
            logging.info("✅ Clicked on the cookie acceptance button.")
        except Exception as ex:
            logging.warning(f"⚠️ Could not click cookie banner: {ex}")

    def expand_shadow_element(self, element):
        """Expands a shadow DOM element."""
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root

    def test_configurator_actions(self):
        url = "https://www.mercedes-benz.at/passengercars/mercedes-benz-cars/car-configurator.html/motorization/CCci/AT/de/GLC-KLASSE/COUPE"
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        time.sleep(3)

        # Handle cookie banner
        self.handle_cookies()

        try:
            # Locate the configurator shadow host
            try:
                shadow_host = self.driver.find_element(By.CSS_SELECTOR, 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owcc-car-configurator')
                logging.info("✅ Shadow host located successfully.")
            except Exception as e:
                logging.error(f"❌ Shadow host not found. Error: {e}")
                return  # Exit the test if the shadow host is not found

            # Expand the shadow root
            try:
                shadow_root = self.expand_shadow_element(shadow_host)
                if shadow_root:
                    logging.info("✅ Shadow root expanded successfully.")
                else:
                    logging.error("❌ Shadow root could not be expanded.")
                    return  # Exit the test if the shadow root is not expanded
            except Exception as e:
                logging.error(f"❌ Failed to expand shadow root. Error: {e}")
                return

            # Locate the specific element within the shadow root
            try:
                target_element = shadow_root.find_element(By.CSS_SELECTOR, '#cc-app-container-main > div.cc-app-container__main-frame.cc-grid-container > div.cc-app-container__navigation.ng-star-inserted > cc-navigation > nav > div > ul')
                logging.info("✅ Target element located successfully within the shadow root.")
            except Exception as e:
                logging.error(f"❌ Target element not found within the shadow root. Error: {e}")
                return

            # Perform actions on the located element (if needed)
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(target_element).perform()
                logging.info('✅ Hovered over the target element.')

                # Click on the target element
                target_element.click()
                logging.info('✅ Clicked on the target element.')
                time.sleep(5)
            except Exception as e:
                logging.error(f"❌ Error performing actions on the target element. Error: {e}")

            # Take a screenshot
            screenshot_filename = "Configurator_Target_Element.png"
            screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), screenshot_filename)
            self.driver.save_screenshot(screenshot_path)
            logging.info(f"📸 Screenshot saved to {screenshot_path}.")
        except Exception as e:
            logging.error(f"❌ Configurator action failed. Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()