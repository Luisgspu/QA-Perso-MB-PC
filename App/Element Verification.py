from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import unittest
import logging
import time
import os
from ConfigCompleted import ConfiguratorCompleted
from CTAHandlerDOM import CTAHandler

class VerifyElements(unittest.TestCase):

    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
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

    def verify_elements(self, url, parent_selector, child_selectors, primary_cta_selector, secondary_cta_selector, expected_primary_href, expected_secondary_href):
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

                    # Perform additional verifications if needed (e.g., check attributes, text, etc.)
                    if child_element.is_displayed():
                        logging.info(f"✅ Child element is visible: {child_selector}")
                    else:
                        logging.warning(f"⚠️ Child element is not visible: {child_selector}")

                except Exception as e:
                    logging.error(f"❌ Child element not found: {child_selector}. Error: {e}")

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
                        logging.info(f"✅ Primary CTA href matches expected value: {expected_primary_href}")
                    else:
                        logging.warning(f"⚠️ Primary CTA href does not match expected value. Expected: {expected_primary_href}, Found: {primary_href}")
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
                        logging.info(f"✅ Secondary CTA href matches expected value: {expected_secondary_href}")
                    else:
                        logging.warning(f"⚠️ Secondary CTA href does not match expected value. Expected: {expected_secondary_href}, Found: {secondary_href}")
                else:
                    logging.warning("⚠️ Secondary CTA is not visible.")
            except Exception as e:
                logging.error(f"❌ Secondary CTA not found. Error: {e}")

        except Exception as e:
            logging.error(f"❌ Parent element not found: {parent_selector}. Error: {e}")
        

    def test_verify_elements(self):
        url = "https://www.mercedes-benz.lu/de/passengercars/models/coupe/cla/overview.html"
        parent_selector = "body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > div.webcomponent.aem-GridColumn.aem-GridColumn--default--12"
        child_selectors = [
            "div > div.owpi-dynamic-stage-mvp__content > div.owpi-dynamic-stage-mvp__options",
            "div > div.owpi-dynamic-stage-mvp__content > div.owpi-dynamic-stage-mvp__options > div > a.wbx-button.wbx-button--secondary.wbx-button--translucent.wbx-button--medium"
        ]
        primary_cta_selector = 'a[class*="primary"][class*="button"]'
        secondary_cta_selector = 'a[class*="secondary"][class*="button"]'

        # Define expected hrefs
        expected_primary_href = "/buy/new-car/search-results.html/"
        expected_secondary_href = "/car-configurator.html/"

        self.verify_elements(url, parent_selector, child_selectors, primary_cta_selector, secondary_cta_selector, expected_primary_href, expected_secondary_href)
                
        '''
        
        try:
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owc-stage')
            shadow_root = self.expand_shadow_element(shadow_host)
            cta_frame = shadow_root.find_element(By.CSS_SELECTOR, 'div > div.owc-stage__content-wrapper > div > div.owc-stage__cta-wrapper.wb-grid-row > div > div')
            
            
            # Hover over the main frame
            actions = ActionChains(self.driver)
            actions.move_to_element(main_frame).perform()
            logging.info('✅ Hovered over Navigation main frame')
            
            # Click on the main frame
            main_frame.click()
            logging.info('✅ Clicked on Navigation main frame')
            time.sleep(5)
        except Exception as e:
            logging.error(f'❌ Could not be clicked. Error: {e}')
            time.sleep(2)
        # Click on CC Summary 
        try:
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owcc-car-configurator')
            shadow_root = self.expand_shadow_element(shadow_host)
            main_frame = shadow_root.find_element(By.CSS_SELECTOR, '#cc-app-container-main > div.cc-app-container__main-frame.cc-grid-container > div.cc-app-container__navigation.ng-star-inserted > cc-navigation > nav > div > ul > li:nth-child(7) > ccwb-text > a')
                
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
        '''    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()