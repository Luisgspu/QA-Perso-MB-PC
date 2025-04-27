# Standard Library Imports
import unittest
import os
import time
import json
import logging
import sys

# Third-Party Imports
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
import requests

# Local Module Imports
from vehicle_api import VehicleAPI  # Importing from the separate module
from ImageVerifier import ImageVerifier  # Importing from the separate module
from ScreenshotHandler import ScreenshotHandler  # Importing from the separate module
from XHRResponseCapturer import XHRResponseCapturer  # Importing from the separate module
from CookiesHandler import CookieHandler  # Importing from the separate module
from CTAHandlerDOM import CTAHandler  # Importing from the separate module
from CTAVerifier import CTAVerifier   # Importing from the separate module  
from TestsCodes import test_bfv1
from TestsCodes import test_bfv2
from TestsCodes import test_bfv3
from TestsCodes import test_LastConfigStarted
from TestsCodes import Test_LastConfigCompleted
from TestsCodes import test_LastSeenSRP
from TestsCodes import test_LastSeenPDP
from TestsCodes import PersonalizedCTA1_test
from TestsCodes import PersonalizedCTA2_test
from TestsCodes import PersonalizedCTA3_test
from TestsCodes import PersonalizedCTA4_test



# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

TARGET_URL_FILTER = "https://daimleragemea.germany-2.evergage.com/"


class TestBFVPC(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--enable-webgl") 
        options.add_argument("--incognito")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--maximize")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        options.add_argument("profile-directory=Default")
        options.add_argument("--start-fullscreen")
        options.add_argument("--no-sandbox")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.fullscreen_window()
        self.vars = {}
        logging.info("✅ Browser opened in headless incognito mode and in full-screen.")

        self.screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests")
        os.makedirs(self.screenshot_dir, exist_ok=True)

        # Initialize VehicleAPI with access token
        self.access_token = "your_api_access_token"
        self.vehicle_api = VehicleAPI(self.access_token)
        
        # Initialize XHRResponseCapturer with default campaign name substring
        self.xhr_capturer = XHRResponseCapturer(self.driver, TARGET_URL_FILTER, "")
        
    def tearDown(self):
        self.driver.quit()
        logging.info("✅ Browser closed.")
    

    def verify_elements(self, url, elements):
        """Verify that specified elements are present on the page."""
        logging.info(f"🔍 Navigating to: {url}")
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

        # Handle cookie banner only once during the test
        cookie_handler = CookieHandler(self.driver)
        cookie_handler.accept_cookies()
        logging.info("✅ Cookies accepted.")
        
        shadow_host = self.driver.find_element(By.CSS_SELECTOR, 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owcc-car-configurator')
        shadow_root = self.expand_shadow_element(shadow_host)
        
        for element in elements:
            try:
                WebDriverWait(shadow_root, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, element)))
                logging.info(f"✅ Element found: {element}")
            except Exception as e:
                logging.error(f"❌ Element not found: {element}. Error: {e}")
    
    def run_test(self, test_name, market_code, model_code, model_name, body_type, attempt, test_link=None, urls=None):
        max_retries = 5
        retries = 0    

        if not urls or 'HOME_PAGE' not in urls or not urls['HOME_PAGE']:
            logging.error(f"❌ Could not fetch valid URLs for test '{test_name}' (market: {market_code}, model: {model_code})")
            return
        
        # Log the fetched URLs from the API
        logging.info(f"🌐 Fetched URLs from API for test '{test_name}': {json.dumps(urls, indent=2)}")

        # BFV Logic
        if 'CONFIGURATOR' not in urls or not urls['CONFIGURATOR']:
            if test_name in ["BFV1", "BFV2", "BFV3", "Last Configuration Started", "Last Configuration Completed"]:
                raise Exception(f"❌ No BFV1, BFV2, BFV3, Last Confifguration Started or Completed possible to test due to lack of CONFIGURATOR URL.")

        if 'ONLINE_SHOP' not in urls or not urls['ONLINE_SHOP']:
            if test_name in ["BFV2", "BFV3", "Last Seen PDP", "Last Seen SRP"]:
                raise Exception(f"❌ No BFV2, BFV3 Or Last Seen PDP SRP possible to test due to lack of ONLINE_SHOP URL.")

        if 'TEST_DRIVE' not in urls or not urls['TEST_DRIVE']:
            if test_name == "BFV3":
                raise Exception(f"❌ No BFV3 possible to test due to lack of TEST_DRIVE URL.")
            
        
        
        test_success = False
        
        

        while retries < max_retries:
            if retries > 0:
                logging.info("♻️ Restarting browser session...")
                self.tearDown()
                self.setUp()

            try:
                self.driver.get(urls['HOME_PAGE'])
                WebDriverWait(self.driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                logging.info(f"🌍 Navigated to: {urls['HOME_PAGE']}")
            except Exception as e:
                logging.error(f"❌ Error navigating to HOME_PAGE: {e}")
                retries += 1
                continue

            # ✅ Always attempt cookie handling
            try:
                WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "cmm-cookie-banner"))
                )
                time.sleep(2)
                logging.info("✅ Cookie banner detected.")
                self.driver.execute_script("""
                    document.querySelector("cmm-cookie-banner").shadowRoot.querySelector("wb7-button.button--accept-all").click();
                """)
                logging.info("✅ Clicked on accept cookies.")
            except Exception as ex:
                logging.info("ℹ️ Cookie banner not found or already accepted.")

            if test_name == "BFV1":
                logging.info(f"🔍 Running BFV1 test... 🔄 Attempt {retries + 1} for BFV1 test")
                bfv1_test_instance = test_bfv1.BFV1Test(self.driver, urls, test_link)
                bfv1_test_instance.run()
                logging.info("✅ BFV1 test completed.")

                time.sleep(4)
                logging.info("🔍 Verifying personalized image...")

                # ✅ Wait for personalized image to appear
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script("""
                            const img = document.querySelector("[data-component-name='hp-campaigns'] img");
                            return img && img.complete && img.naturalHeight !== 0 && img.src.includes("/content/dam/hq/personalization/campaignmodule/");
                        """)
                    )
                    image_found = True
                except Exception:
                    image_found = False

                # 🔍 Debug log of images (always helpful)
                try:
                    imgs = self.driver.execute_script("""
                        return Array.from(document.querySelectorAll("[data-component-name='hp-campaigns'] img")).map(img => img.src);
                    """)
                    logging.info(f"🖼️ Found campaign images: {imgs}")
                except Exception as e:
                    logging.error(f"❌ Error extracting campaign images: {e}")

                if image_found:
                    logging.info("✅ Personalized image was applied correctly.")
                    test_success = True
                
                else:
                    logging.warning("⚠️ Personalized image was NOT applied correctly.")
                     # ✅ XHR Capture — always attempt
                    logging.info("🔍 Capturando respuestas XHR...")
                    self.xhr_capturer.set_campaign_name_substring(test_name)
                    self.xhr_capturer.capture_responses()
                    # ✅ Save captured XHR responses to file
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")
                # 📸 Screenshot
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)
                
                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break
                           
            elif test_name == "BFV2":
                logging.info(f"🔍 Running BFV2 test... 🔄 Attempt {retries + 1} for BFV2 test")
                # Assuming BFV2Test is another test class, instantiate and run it
                bfv2_test_instance = test_bfv2.BFV2Test(self.driver, urls, test_link)
                bfv2_test_instance.run()
                logging.info("✅ BFV2 test completed.")

                time.sleep(4)
                logging.info("🔍 Verifying personalized image...")

                # ✅ Wait for personalized image to appear
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script("""
                            const img = document.querySelector("[data-component-name='hp-campaigns'] img");
                            return img && img.complete && img.naturalHeight !== 0 && img.src.includes("/content/dam/hq/personalization/campaignmodule/");
                        """)
                    )
                    image_found = True
                except Exception:
                    image_found = False

                if image_found:
                    logging.info("✅ Personalized image was applied correctly.")
                    test_success = True
                    
                else:
                    logging.warning("⚠️ Personalized image was NOT applied correctly.")
                    # ✅ XHR Capture — always attempt
                    logging.info("🔍 Capturando respuestas XHR...")
                    self.xhr_capturer.capture_responses()
                    # ✅ Save captured XHR responses to file
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")
                # 📸 Screenshot
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)
                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break    
                
            elif test_name == "BFV3":
                logging.info(f"🔍 Running BFV3 test... 🔄 Attempt {retries + 1} for BFV3 test")
                bfv3_test_instance = test_bfv3.BFV3Test(self.driver, urls, test_link)
                bfv3_test_instance.run()
                logging.info("✅ BFV3 test completed.") 
                
                time.sleep(4)
                logging.info("🔍 Verifying personalized image...")

                # ✅ Wait for personalized image to appear
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script("""
                            const img = document.querySelector("[data-component-name='hp-campaigns'] img");
                            return img && img.complete && img.naturalHeight !== 0 && img.src.includes("/content/dam/hq/personalization/campaignmodule/");
                        """)
                    )
                    image_found = True
                except Exception:
                    image_found = False

                if image_found:
                    logging.info("✅ Personalized image was applied correctly.")
                    test_success = True
                    # 📸 Screenshot
                    logging.info("📸 Taking screenshot...")
                    scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                    scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)

                else:
                    logging.warning("⚠️ Personalized image was NOT applied correctly.")
                    # ✅ XHR Capture — always attempt
                    logging.info("🔍 Capturando respuestas XHR...")
                    self.xhr_capturer.capture_responses()
                    # ✅ Save captured XHR responses to file
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")
                # 📸 Screenshot
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)        
                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break    
                
            elif test_name == "Last Configuration Started":
                logging.info(f"🔍 Running Last Configuration Started test... 🔄 Attempt {retries + 1} for Last Configuration Started test")
                lc_started_test_instance = test_LastConfigStarted.LCStartedTest(self.driver, urls, test_link)
                lc_started_test_instance.run()
                logging.info("✅ Last Configuration Started test completed.")
                
                time.sleep(4)
                logging.info("🔍 Verifying personalized image...")

                # ✅ Wait for personalized image to appear
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script("""
                            const img = document.querySelector("[data-component-name='hp-campaigns'] img");
                            return img && img.complete && img.naturalHeight !== 0 && img.src.includes("/images/dynamic/europe/");
                        """)
                    )
                    image_found = True
                except Exception:
                    image_found = False

                if image_found:
                    logging.info("✅ Personalized image was applied correctly.")
                    test_success = True

                else:
                    logging.warning("⚠️ Personalized image was NOT applied correctly.")
                    # ✅ XHR Capture — always attempt
                    logging.info("🔍 Capturando respuestas XHR...")
                    self.xhr_capturer.set_campaign_name_substring(test_name)
                    self.xhr_capturer.capture_responses()
                    # ✅ Save captured XHR responses to file
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")
                # 📸 Screenshot
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)        
                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break 
            
            elif test_name == "Last Configuration Completed":
                logging.info(f"🔍 Running Last Configuration Completed test... 🔄 Attempt {retries + 1} for Last Configuration Completed test")
                lc_started_test_instance = Test_LastConfigCompleted.LCCompletedTest(self.driver, urls, test_link)
                lc_started_test_instance.run()
                logging.info("✅ Last Configuration Completed test completed.")
                
                time.sleep(4)
                logging.info("🔍 Verifying personalized image...")

                # ✅ Wait for personalized image to appear
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script("""
                            const img = document.querySelector("[data-component-name='hp-campaigns'] img");
                            return img && img.complete && img.naturalHeight !== 0 && img.src.includes("/images/dynamic/europe/");
                        """)
                    )
                    image_found = True
                except Exception:
                    image_found = False

                if image_found:
                    logging.info("✅ Personalized image was applied correctly.")
                    test_success = True
                    
                else:
                    logging.warning("⚠️ Personalized image was NOT applied correctly.")
                    # ✅ XHR Capture — always attempt
                    logging.info("🔍 Capturando respuestas XHR...")
                    self.xhr_capturer.capture_responses()
                    # ✅ Save captured XHR responses to file
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")
                # 📸 Screenshot
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)    
                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break
                
            elif test_name == "Last Seen SRP":
                logging.info(f"🔍 Running Last Seen SRP test... 🔄 Attempt {retries + 1} for Last Seen SRP test")
                last_seen_srp_test_instance = test_LastSeenSRP.LSeenSRPTest(self.driver, urls, test_link)
                last_seen_srp_test_instance.run()
                logging.info("✅ Last Seen SRP test completed.")
                time.sleep(4)
                logging.info("🔍 Verifying personalized image...")

                # ✅ Wait for personalized image to appear
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script("""
                            const img = document.querySelector("[data-component-name='hp-campaigns'] img");
                            return img && img.complete && img.naturalHeight !== 0 && img.src.includes("/images/dynamic/europe/");
                        """)
                    )
                    image_found = True
                except Exception:
                    image_found = False

                if image_found:
                    logging.info("✅ Personalized image was applied correctly.")
                    test_success = True
    
                else:
                    logging.warning("⚠️ Personalized image was NOT applied correctly.")
                    # ✅ XHR Capture — always attempt
                    logging.info("🔍 Capturando respuestas XHR...")
                    self.xhr_capturer.set_campaign_name_substring(test_name)
                    self.xhr_capturer.capture_responses()
                    # ✅ Save captured XHR responses to file
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")
                # 📸 Screenshot
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success) 
                           
                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break              
            
            elif test_name == "Last Seen PDP":
                logging.info(f"🔍 Running Last Seen PDP test... 🔄 Attempt {retries + 1} for Last Seen PDP test")
                last_seen_srp_test_instance = test_LastSeenPDP.LSeenPDPTest(self.driver, urls, test_link)
                last_seen_srp_test_instance.run()
                logging.info("✅ Last Seen PDP test completed.")
                
                time.sleep(4)
                logging.info("🔍 Verifying personalized image...")

                # ✅ Wait for personalized image to appear
                try:
                    WebDriverWait(self.driver, 10).until(
                        lambda d: d.execute_script("""
                            const img = document.querySelector("[data-component-name='hp-campaigns'] img");
                            return img && img.complete && img.naturalHeight !== 0 && img.src.includes("/images/dynamic/europe/");
                        """)
                    )
                    image_found = True
                except Exception:
                    image_found = False

                if image_found:
                    logging.info("✅ Personalized image was applied correctly.")
                    test_success = True
                    
                else:
                    logging.warning("⚠️ Personalized image was NOT applied correctly.")
                    # ✅ XHR Capture — always attempt
                    logging.info("🔍 Capturando respuestas XHR...")
                    self.xhr_capturer.capture_responses()
                    # ✅ Save captured XHR responses to file
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")
                # 📸 Screenshot
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)
                        
                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break                  
                
            elif test_name == "Personalized CTA Affinity":
                logging.info(f"🔍 Running Personalized CTA Affinity test... 🔄 Attempt {retries + 1} for Personalized CTA Affinity test")
                personalized_cta_test_instance = PersonalizedCTA1_test.PersonalizedCTA1Test(self.driver, urls, test_link)
                personalized_cta_test_instance.run()
                logging.info("✅ Personalized CTA Affinity test completed.")
                
                time.sleep(4)
                logging.info("🔍 Verifying personalized CTAs...")

                try:
                    # Use CTAHandler to verify the CTAs
                    time.sleep(4)  # Optional: wait for elements to load
                    cta_handler = CTAHandler(self.driver)

                    # Define selectors
                    shadow_host_selector = 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owc-stage'
                    fallback_parent_selector = 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > div.webcomponent.aem-GridColumn.aem-GridColumn--default--12'
                    parent_selector = 'div > div.owc-stage__content-wrapper > div > div.owc-stage__cta-wrapper.wb-grid-row > div > div'
                    primary_cta_selector = 'a[class*="primary"][class*="button"]'
                    secondary_cta_selector = 'a[class*="secondary"][class*="button"]'

                    # Define expected hrefs
                    expected_primary_href = "/buy/new-car/search-results.html/"
                    expected_secondary_href = "#contact"

                    # Verify CTAs using CTAHandler
                    cta_changed = cta_handler.verify_ctas(
                        shadow_host_selector,
                        parent_selector,
                        fallback_parent_selector,
                        primary_cta_selector,
                        secondary_cta_selector,
                        expected_primary_href,
                        expected_secondary_href
                    )

                    if cta_changed:
                        logging.info("✅ Personalized CTAs verified successfully using CTAHandler.")
                        test_success = True
                    else:
                        logging.warning("⚠️ Personalized CTAs verification failed using CTAHandler.")
                        test_success = False
                except Exception as e:
                    logging.error(f"❌ Error verifying personalized CTA: {e}")
                    test_success = False

                # Take a screenshot regardless of success or failure
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)

                # If the test failed, capture XHR responses
                if not test_success:
                    logging.info("🔍 Capturing XHR responses...")
                    self.xhr_capturer.set_campaign_name_substring(test_name)
                    self.xhr_capturer.capture_responses()
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")

                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break        
                
            elif test_name == "Personalized CTA OWCC":
                logging.info(f"🔍 Running Personalized CTA OWCC test... 🔄 Attempt {retries + 1} for Personalized CTA OWCC test")
                personalized_cta_test_instance = PersonalizedCTA2_test.PersonalizedCTA2Test(self.driver, urls, test_link)
                personalized_cta_test_instance.run()
                logging.info("✅ Personalized CTA OWCC test completed.")
                
                logging.info("🔍 Verifying personalized CTAs...")

                try:
                    # Use CTAHandler to verify the CTAs
                    time.sleep(4)  # Optional: wait for elements to load
                    cta_handler = CTAHandler(self.driver)

                    # Define selectors
                    shadow_host_selector = 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owc-stage'
                    fallback_parent_selector = 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > div.webcomponent.aem-GridColumn.aem-GridColumn--default--12'
                    parent_selector = 'div > div.owc-stage__content-wrapper > div > div.owc-stage__cta-wrapper.wb-grid-row > div > div'
                    primary_cta_selector = 'a[class*="primary"][class*="button"]'
                    secondary_cta_selector = 'a[class*="secondary"][class*="button"]'

                    # Define expected hrefs
                    expected_primary_href = "/buy/new-car/search-results.html/"
                    expected_secondary_href = "/online-testdrive.html#/"

                    # Verify CTAs using CTAHandler
                    cta_changed = cta_handler.verify_ctas(
                        shadow_host_selector,
                        parent_selector,
                        fallback_parent_selector,
                        primary_cta_selector,
                        secondary_cta_selector,
                        expected_primary_href,
                        expected_secondary_href
                    )

                    if cta_changed:
                        logging.info("✅ Personalized CTAs verified successfully using CTAHandler.")
                        test_success = True
                    else:
                        logging.warning("⚠️ Personalized CTAs verification failed using CTAHandler.")
                        test_success = False
                except Exception as e:
                    logging.error(f"❌ Error verifying personalized CTA: {e}")
                    test_success = False
                    
                # Take a screenshot regardless of success or failure
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)

                # If the test failed, capture XHR responses
                if not test_success:
                    logging.info("🔍 Capturing XHR responses...")
                    self.xhr_capturer.set_campaign_name_substring(test_name)
                    self.xhr_capturer.capture_responses()
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")

                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break        
                    
            elif test_name == "Personalized CTA PDP":
                logging.info(f"🔍 Running Personalized CTA PDP... 🔄 Attempt {retries + 1} for Personalized CTA PDP test")
                personalized_cta_test_instance = PersonalizedCTA3_test.PersonalizedCTA3Test(self.driver, urls, test_link)
                personalized_cta_test_instance.run()
                logging.info("✅ Personalized CTA PDP test completed.")
                
                logging.info("🔍 Verifying personalized CTAs...")

                try:
                    # Use CTAHandler to verify the CTAs
                    time.sleep(4)  # Optional: wait for elements to load
                    cta_handler = CTAHandler(self.driver)

                    # Define selectors
                    shadow_host_selector = 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owc-stage'
                    fallback_parent_selector = 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > div.webcomponent.aem-GridColumn.aem-GridColumn--default--12'
                    parent_selector = 'div > div.owc-stage__content-wrapper > div > div.owc-stage__cta-wrapper.wb-grid-row > div > div'
                    primary_cta_selector = 'a[class*="primary"][class*="button"]'
                    secondary_cta_selector = 'a[class*="secondary"][class*="button"]'

                    # Define expected hrefs
                    expected_primary_href = "/buy/new-car/product.html/"
                    expected_secondary_href = "/car-configurator.html/"

                    # Verify CTAs using CTAHandler
                    cta_changed = cta_handler.verify_ctas(
                        shadow_host_selector,
                        parent_selector,
                        fallback_parent_selector,
                        primary_cta_selector,
                        secondary_cta_selector,
                        expected_primary_href,
                        expected_secondary_href
                    )

                    if cta_changed:
                        logging.info("✅ Personalized CTAs verified successfully using CTAHandler.")
                        test_success = True
                    else:
                        logging.warning("⚠️ Personalized CTAs verification failed using CTAHandler.")
                        test_success = False
                except Exception as e:
                    logging.error(f"❌ Error verifying personalized CTA: {e}")
                    test_success = False
            
                # Take a screenshot regardless of success or failure
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)

                # If the test failed, capture XHR responses
                if not test_success:
                    logging.info("🔍 Capturing XHR responses...")
                    self.xhr_capturer.set_campaign_name_substring(test_name)
                    self.xhr_capturer.capture_responses()
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")

                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break    
                    
            elif test_name == "Personalized CTA OWCC + PDP":
                logging.info(f"🔍 Running Personalized CTA OWCC + PDP... 🔄 Attempt {retries + 1} for Personalized CTA OWCC + PDP test")
                personalized_cta_test_instance = PersonalizedCTA4_test.PersonalizedCTA4Test(self.driver, urls, test_link)
                personalized_cta_test_instance.run()
                logging.info("✅ Personalized CTA OWCC + PDP test completed.")
                
                logging.info("🔍 Verifying personalized CTAs...")

                try:
                    # Use CTAHandler to verify the CTAs
                    time.sleep(4)  # Optional: wait for elements to load
                    cta_handler = CTAHandler(self.driver)

                    # Define selectors
                    shadow_host_selector = 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owc-stage'
                    fallback_parent_selector = 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > div.webcomponent.aem-GridColumn.aem-GridColumn--default--12'
                    parent_selector = 'div > div.owc-stage__content-wrapper > div > div.owc-stage__cta-wrapper.wb-grid-row > div > div'
                    primary_cta_selector = 'a[class*="primary"][class*="button"]'
                    secondary_cta_selector = 'a[class*="secondary"][class*="button"]'

                    # Define expected hrefs
                    expected_primary_href = "/buy/new-car/product.html/"
                    expected_secondary_href = "/finance/"

                    # Verify CTAs using CTAHandler
                    cta_changed = cta_handler.verify_ctas(
                        shadow_host_selector,
                        parent_selector,
                        fallback_parent_selector,
                        primary_cta_selector,
                        secondary_cta_selector,
                        expected_primary_href,
                        expected_secondary_href
                    )

                    if cta_changed:
                        logging.info("✅ Personalized CTAs verified successfully using CTAHandler.")
                        test_success = True
                    else:
                        logging.warning("⚠️ Personalized CTAs verification failed using CTAHandler.")
                        test_success = False
                except Exception as e:
                    logging.error(f"❌ Error verifying personalized CTA: {e}")
                    test_success = False
            
                # Take a screenshot regardless of success or failure
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)

                # If the test failed, capture XHR responses
                if not test_success:
                    logging.info("🔍 Capturing XHR responses...")
                    self.xhr_capturer.set_campaign_name_substring(test_name)
                    self.xhr_capturer.capture_responses()
                    try:
                        xhr_data = self.xhr_capturer.get_captured_data()
                        xhr_filename = f"xhr_responses_{test_name}_{model_name}_{body_type}_attempt_{retries + 1}.json"
                        xhr_path = os.path.join(self.screenshot_dir, xhr_filename)

                        with open(xhr_path, "w", encoding="utf-8") as f:
                            json.dump(xhr_data, f, indent=2, ensure_ascii=False)

                        logging.info(f"📁 Saved XHR responses to: {xhr_path}")
                    except Exception as e:
                        logging.error(f"❌ Failed to save XHR responses: {e}")

                if test_success:
                    logging.info(f"✅ Test '{test_name}' passed on attempt {retries + 1}")
                    break    
                    
                # 📸 Screenshot
                logging.info("📸 Taking screenshot...")
                scroll_and_capture_screenshot = ScreenshotHandler(self.driver, self.screenshot_dir)
                scroll_and_capture_screenshot.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)
                
            retries += 1

        if retries == max_retries:
            logging.error(f"❌ Test '{test_name}' failed after {max_retries} attempts.")


def run_selected_tests(test_cases, iterations):
    suite = unittest.TestSuite()
    for test_case in test_cases:
        # Fetch URLs once for the entire test case
        market_code = test_case.get('market_code', 'BE/nl')  # Default market code if not provided
        model_code = test_case.get('model_code', '')
        
        # Only fetch URLs once per test
        test_instance = TestBFVPC()
        test_instance.setUp()  # Set up once per test case
        try:
            urls = test_instance.vehicle_api.fetch_urls_from_api(market_code, model_code)
            if urls and 'MODEL_NAME' in urls and 'BODY_TYPE' in urls:
                for attempt in range(1, iterations + 1):
                    try:
                        test_instance.run_test(
                            test_case['test_name'],
                            market_code,
                            model_code,
                            urls['MODEL_NAME'],
                            urls['BODY_TYPE'],
                            attempt,
                            test_case.get('Test_link'),
                            urls=urls  # Pass the fetched URLs to the test method
                        )
                    except Exception as e:
                        logging.error(f"❌ Exception occurred during test '{test_case['test_name']}': {e}")
                        break  # Stop retrying this test and move to the next one
            else:
                logging.error(f"❌ Test '{test_case['test_name']}' skipped due to missing MODEL_NAME or BODY_TYPE.")
        except Exception as e:
            logging.error(f"❌ Failed to set up test '{test_case['test_name']}': {e}")
        finally:
            test_instance.tearDown()  # Tear down once per test case



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    tests = [

     
    {
        "test_name": "Last Configuration Started",
        "market_code": "IT/it",
        "model_code": "C236"
    
    },


    
 

    
        # Add more tests as needed
    ]
    
    # Set the number of iterations for all test cases
    iterations =  1  # Number of iterations to run each test
    run_selected_tests(tests, iterations)
    