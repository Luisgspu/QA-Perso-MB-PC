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
        #options.add_argument('--headless')
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

    def verify_elements(self, url, elements):
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        # Handle cookie banner if present
        self.handle_cookies()
        time.sleep(2)  # Optional: wait for the cookies to be accepted
        
        self.driver.get("https://www.mercedes-benz.lu/de/passengercars/mercedes-benz-cars/car-configurator.html/motorization/CCci/LU/de/EQA-KLASSE/OFFROADER")    
        # Reload the page to ensure the cookies are accepted
        time.sleep(4)  # Optional: wait for the page to load again
        
        # Initialize ConfiguratorCompleted
        configurator = ConfiguratorCompleted(self.driver)
        
        # Call the perform_configurator_actions method
        configurator.perform_configurator_actions()
        
        logging.info("✅ Completed actions in the configurator.")
        
        self.driver.get(url)
        time.sleep(4)  # Optional: wait for the page to load again
        
        # Initialize ShadowHostHandler
        shadow_handler = CTAHandler(self.driver)

        # Define selectors
        shadow_host_selector = 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owc-stage'
        parent_selector = 'div > div.owc-stage__content-wrapper > div > div.owc-stage__cta-wrapper.wb-grid-row > div > div'
        primary_cta_selector = 'a[class*="primary"][class*="button"]'
        secondary_cta_selector = 'a[class*="secondary"][class*="button"]'

        # Verify CTAs using ShadowHostHandler
        shadow_handler.verify_ctas(
            shadow_host_selector,
            parent_selector,
            primary_cta_selector,
            secondary_cta_selector
    )
        
        
        
        '''
        # Step 1: Locate the shadow host
        try:
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owc-stage')
            shadow_root = self.expand_shadow_element(shadow_host)
            logging.info("✅ Shadow host located and shadow root expanded.")
        except Exception as e:
            logging.error(f"❌ Shadow host not found: {e}")
            return
        
        # Step 2: Verify elements within the shadow DOM
        try:
            parent_element = shadow_root.find_element(By.CSS_SELECTOR, 'div > div.owc-stage__content-wrapper > div > div.owc-stage__cta-wrapper.wb-grid-row > div > div')
            logging.info("✅ Parent element located.")
        except Exception as e:
            logging.error(f"❌ Parent element not found: {e}")
            return
        
        time.sleep(3)  # Optional: wait for the elements to load
        
        # Step 3: Locate the Primary CTA child element within the parent element
        try:
            specific_cta = parent_element.find_element(By.CSS_SELECTOR, 'a[class*="primary"][class*="button"]')
            logging.info("✅ Primary CTA element located.")
            
            # Verify if the href includes "/buy/new-car/search-results.html/"
            href_value = specific_cta.get_attribute("href")
            if "/buy/new-car/search-results.html/" in href_value:
                logging.info(f"✅ The href attribute includes '/buy/new-car/search-results.html/': {href_value}")
            else:
                logging.warning(f"⚠️ The href attribute does not include '/buy/new-car/search-results.html/': {href_value}")
                
            
            # Optionally, interact with the CTA (e.g., click it)
            specific_cta.click()
            logging.info("✅ Specific CTA element clicked.")
        
        except Exception as e:
            logging.error(f"❌ Primary CTA element not found: {e}")
            return    
                
        # Step 4: Locate the Secondary CTA child element within the parent element
        try:
            specific_cta = parent_element.find_element(By.CSS_SELECTOR, 'a[class*="secondary"][class*="button"]')
            logging.info("✅ Secondary CTA element located.")
            
            # Verify if the href includes "/car-configurator.html/"
            href_value = specific_cta.get_attribute("href")
            if "/online-testdrive.html#/" in href_value:
                logging.info(f"✅ The href attribute includes '/car-configurator.html/': {href_value}")
            else:
                logging.warning(f"⚠️ The href attribute does not include '/online-testdrive.html#/': {href_value}")
                
            
            # Optionally, interact with the CTA (e.g., click it)
            specific_cta.click()
            logging.info("✅ Specific CTA element clicked.")
        
        except Exception as e:
            logging.error(f"❌ Secondary CTA element not found: {e}")
            return    
        
        '''

    def test_verify_elements(self):
        urls_y_elements = {
            'https://www.mercedes-benz.lu/de/passengercars/models/suv/eqa/overview.html': [
                'div > div.owc-stage__content-wrapper > div > div.owc-stage__cta-wrapper.wb-grid-row > div > div > a.owc-stage-cta-buttons__button.wb-button.wb-button--medium.wb-button--large.wb-button--secondary.owc-stage-cta-buttons__button--secondary'
            ]
        }

        for url, elements in urls_y_elements.items():
            self.verify_elements(url, elements)
            
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