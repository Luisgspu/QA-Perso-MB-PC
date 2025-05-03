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

    def verify_elements(self, url, parent_selector):
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        # Handle cookie banner if present
        self.handle_cookies()
        time.sleep(2)  # Optional: wait for the cookies to be accepted
         
        try:
            # Locate the shadow host
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, parent_selector)
            logging.info("✅ Shadow host located successfully.")

            # Expand the shadow root
            shadow_root = self.expand_shadow_element(shadow_host)
            logging.info("✅ Shadow root expanded successfully.")

            # Locate the main frame (ul element)
            main_frame = shadow_root.find_element(By.CSS_SELECTOR, '#cc-app-container-main > div.cc-app-container__main-frame.cc-grid-container > div.cc-app-container__navigation.ng-star-inserted > cc-navigation > nav > div > ul')
            main_frame.click()
            time.sleep(2)  # Optional: wait for any action to complete
            logging.info("✅ Main frame (ul element) located successfully.")


            # Locate all child elements (li elements) inside the main frame
            child_elements = main_frame.find_elements(By.CSS_SELECTOR, 'li')
            if child_elements:
                logging.info(f"✅ Child elements located successfully. Total children: {len(child_elements)}")

                # Click the second child element if it exists
                if len(child_elements) > 1:  # Ensure there is a second child
                    second_child = child_elements[1]  # Get the second child element (index 1)
                    logging.info(f"✅ Second child (li element) located successfully.")
                    logging.info(f"🔍 Second child element details: {second_child.get_attribute('outerHTML')}")

                    # Scroll the second child into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", second_child)
                    logging.info('✅ Second child (li element) scrolled into view.')

                    # Hover over the second child
                    actions = ActionChains(self.driver)
                    actions.move_to_element(second_child).perform()
                    logging.info('✅ Hovered over the second child (li element).')

                    # Click the second child
                    second_child.click()
                    time.sleep(2)  # Optional: wait for any action to complete
                    logging.info('✅ Clicked on the second child (li element).')
                else:
                    logging.warning("⚠️ Less than 2 child elements found. Skipping click on the second child.")

                # Click the last child element
                last_child = child_elements[-1]  # Get the last child element
                logging.info(f"✅ Last child (li element) located successfully.")
                logging.info(f"🔍 Last child element details: {last_child.get_attribute('outerHTML')}")

                # Scroll the last child into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", last_child)
                logging.info('✅ Last child (li element) scrolled into view.')

                # Hover over the last child
                actions.move_to_element(last_child).perform()
                logging.info('✅ Hovered over the last child (li element).')

                # Click the last child
                last_child.click()
                time.sleep(2)  # Optional: wait for any action to complete
                logging.info('✅ Clicked on the last child (li element).')
            else:
                logging.error("❌ No child elements found inside the main frame (ul element).")
            
        except Exception as e:
            logging.error(f"❌ Error during element verification. Error: {e}")
    
        

    def test_verify_elements(self):
        url = "https://www.mercedes-benz.at/passengercars/mercedes-benz-cars/car-configurator.html/motorization/CCci/AT/de/EQE-KLASSE/OFFROADER"
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