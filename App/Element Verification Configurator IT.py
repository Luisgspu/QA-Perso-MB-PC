from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import unittest
import logging
import time
import os
from ImageVerifier  import ImageVerifier

class VerifyElements(unittest.TestCase):

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
            WebDriverWait(self.driver, 30).until(
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
        try:
            return self.driver.execute_script('return arguments[0].shadowRoot', element)
        except Exception as e:
            logging.warning(f"⚠️ No se pudo expandir shadowRoot: {e}")
            return None

    def verify_elements(self, url, parent_selector):
        self.driver.get(url)
        WebDriverWait(self.driver, 30).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

        # Manejo de cookies
        time.sleep(2)
        self.handle_cookies()
        time.sleep(2)
        self.driver.get("https://www.mercedes-benz.it/passengercars/models/saloon/s-class/overview.html")
        time.sleep(2)
        self.driver.get(url)
        time.sleep(2)

        self.image_verifier = ImageVerifier(self.driver)
        
        # Call the image verifier here
        result = self.image_verifier.verify_image(
            selector="[data-component-name='hp-campaigns'] img",           # <-- update this selector
            expected_path="/content/dam/hq/personalization/campaignmodule/",    # <-- update this expected path
            test_name="test_verify_elements"
        )
        # Optionally, assert or log the result
        self.assertTrue(result, "Expected image was not found on the page.")
        time.sleep(2)


        
        

    def test_verify_elements(self):
        url = "https://www.mercedes-benz.it"
        parent_selector = "body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owcc-car-configurator"
        



        self.verify_elements(url, parent_selector)
                
        
        
       
            
        """
        # Click on CC Summary
        try:
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owcc-car-configurator')
            shadow_root = self.expand_shadow_element(shadow_host)
            main_frame = shadow_root.find_element(By.CSS_SELECTOR, '#cc-app-container-main > div.cc-app-container__main-frame.cc-grid-container > div.cc-app-container__navigation.ng-star-inserted > cc-navigation > nav > div > ul > last-child(7)')
                
            # Hover over the main frame
            actions = ActionChains(self.driver)
            actions.move_to_element(main_frame).perform()
            logging.info('✅ Hovered over to CC Summary')
                
            # Click on the main frame
            main_frame.click()
            logging.info('✅ Clicked on CC Summary')
            time.sleep(5)
        except Exception as e:
            logging.error(f'❌ CC Summary could not be clicked. Error: {e}')
            time.sleep(2)
        # Take a screenshot
        try:
            screenshot_filename = f"Last Element Clicked.png"
            screenshot_path = os.path.join(self.screenshot_dir, screenshot_filename)
            self.driver.save_screenshot(screenshot_path)
            logging.info(f"📸 Screenshot saved to {screenshot_path}.")
        except Exception as e:
            logging.info("⚠️ Cookies were not accepted, elements could not be verified or clicked.")
        """

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()