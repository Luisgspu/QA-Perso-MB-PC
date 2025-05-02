from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import unittest
import logging
import time
import os

class VerifyElements(unittest.TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') # Uncomment this line to run in headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--enable-webgl")
        options.add_argument("--maximize")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        options.add_argument("profile-directory=Default")
        options.add_argument("--start-fullscreen")
        self.driver = webdriver.Chrome(options=options)
        self.driver.fullscreen_window()
        self.vars = {}
        logging.info("✅ Browser opened in headless mode and in full-screen.")

        self.screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Element Verification")
        os.makedirs(self.screenshot_dir, exist_ok=True)

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
        shadow_root = self.driver.execute_script('return arguments[0].shadowRoot', element)
        return shadow_root

    def verify_elements(self, url, parent_selector, child_selectors):
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        # Handle cookie banner if present
        self.handle_cookies()
        time.sleep(2)  # Optional: wait for the cookies to be accepted

        try:
            # Locate the parent element
            parent_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, parent_selector))
            )
            logging.info("✅ Parent element located.")

            # Iterate through the child selectors and verify each child element
            for child_selector in child_selectors:
                try:
                    child_element = parent_element.find_element(By.CSS_SELECTOR, child_selector)
                    logging.info(f"✅ Child element located: {child_selector}")

                    # Scroll to the child element
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", child_element)
                    logging.info(f"✅ Scrolled to child element: {child_selector}")

                    # Perform additional verifications if needed (e.g., check attributes, text, etc.)
                    if child_element.is_displayed():
                        logging.info(f"✅ Child element is visible: {child_selector}")
                    else:
                        logging.warning(f"⚠️ Child element is not visible: {child_selector}")

                    # Debug campaign images within the child element
                    time.sleep(3)  # Optional: wait for the images to load
                    try:
                        WebDriverWait(self.driver, 30).until(
                            lambda d: d.execute_script("""
                                const child = arguments[0];
                                return Array.from(child.querySelectorAll("img")).every(img => img.complete && img.naturalHeight > 0);
                            """, child_element)
                        )
                        imgs = self.driver.execute_script("""
                            const child = arguments[0];
                            return Array.from(child.querySelectorAll("img")).map(img => img.src);
                        """, child_element)
                        logging.info(f"🖼️ Found images in child element: {child_selector} - {imgs}")
                    except Exception as e:
                        logging.error(f"❌ Error extracting image URLs from child element '{child_selector}': {e}")
                except Exception as e:
                    logging.error(f"❌ Child element not found: {child_selector}. Error: {e}")

        except Exception as e:
            logging.error(f"❌ Parent element not found: {parent_selector}. Error: {e}")

    def test_verify_elements(self):
        url = "https://www.mercedes-benz.co.uk/"
        parent_selector = "body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > div:nth-child(14)"
        child_selectors = [
            "body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > div:nth-child(14) > div"
        ]

        self.verify_elements(url, parent_selector, child_selectors)
                    
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()