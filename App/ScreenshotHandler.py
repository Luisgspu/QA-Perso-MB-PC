import os
import time
from selenium.webdriver.common.by import By
import allure

class ScreenshotHandler:
    def __init__(self, driver, screenshot_dir):
        self.driver = driver
        self.screenshot_dir = screenshot_dir

    def scroll_and_capture_screenshot(self, urls, test_name, model_name, body_type, retries, test_success):
        """Scrolls through the page, captures screenshots, and handles specific market scrolling logic."""
        try:
            # Determine the status of the test
            status = "SUCCESSFUL" if test_success else "UNSUCCESSFUL"
            
            # Extract the market code and language code
            market_code = self.get_market_code(urls['HOME_PAGE'])
            language_code = self.get_language_code(urls['HOME_PAGE'])
            
            # Construct the filename
            market_code = self.get_market_code(urls['HOME_PAGE'])
            filename = f"{market_code}-{language_code}-{test_name} {model_name} {body_type} {retries + 1} {status}.png"
            filepath = os.path.join(self.screenshot_dir, filename)

            with allure.step("📜 Scrolling to specific elements and capturing screenshot"):
                # Scroll to the main campaign element
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, "[data-component-name='hp-campaigns']")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'start'});", element)
                    time.sleep(3)
                    allure.attach("✅ Scrolled to [data-component-name='hp-campaigns'].", name="Scroll Info", attachment_type=allure.attachment_type.TEXT)
                except Exception as e:
                    allure.attach(f"❌ Error: {e}", name="Scroll Error", attachment_type=allure.attachment_type.TEXT)

                # Handle specific market scrolling logic
                try:
                    if ".fr" in urls['HOME_PAGE']:
                        hp_element = self.driver.find_element(By.CSS_SELECTOR, 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > div:nth-child(13) > div > div.wb-grid-container > h2')
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'start'});", hp_element)
                        time.sleep(2)
                        allure.attach("Scrolled to the French market-specific element.", name="Scroll Info (FR)", attachment_type=allure.attachment_type.TEXT)

                    if ".hu" in urls['HOME_PAGE']:
                        hp_element = self.driver.find_element(By.CSS_SELECTOR, 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > div:nth-child(11) > div > div.wb-grid-container > h2')
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'start'});", hp_element)
                        time.sleep(2)
                        allure.attach("✅ Scrolled to the Hungarian market-specific element.", name="Scroll Info (HU)", attachment_type=allure.attachment_type.TEXT)
                except Exception as e:
                    allure.attach(f"Error: {e}", name="Market Scroll Error", attachment_type=allure.attachment_type.TEXT)

            # Capture and save the screenshot
            self.driver.save_screenshot(filepath)
            with allure.step("✅ Screenshot captured and saved"):
                allure.attach.file(filepath, name="Final Screenshot", attachment_type=allure.attachment_type.PNG)

        except Exception as e:
            with allure.step("❌ Error capturing screenshot"):
                allure.attach(f"Error saving or attaching screenshot: {e}", name="Error", attachment_type=allure.attachment_type.TEXT)

    def get_language_code(self, url):
        """Extracts the language code from the URL."""
        if "/fr" in url:
            return "fr"
        elif "/de" in url:
            return "de"
        elif "/it" in url:
            return "it"
        elif "/nl" in url:
            return "nl"
        else:
            return ""

    def get_market_code(self, url):
        """Extracts the market code from the URL."""
        domain_map = {
            ".ro": "ro", ".de": "de", ".at": "at", ".pt": "pt", ".be": "be",
            ".co.uk": "co_UK", ".hu": "hu", ".es": "es", ".it": "it", ".pl": "pl",
            ".nl": "nl", ".fr": "fr", ".lu": "lu", ".dk": "dk", ".cz": "cz",
            ".ch": "ch", ".se": "se", ".sk": "sk"
        }
        for domain, code in domain_map.items():
            if domain in url:
                return code
        return "unknown"

    @staticmethod
    def attach_screenshot_to_allure(screenshot_path):
        """Attaches a screenshot to the Allure report."""
        try:
            with allure.step("Attaching screenshot to Allure"):
                with open(screenshot_path, 'rb') as file:
                    allure.attach(file.read(), name="Screenshot", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(f"Error attaching screenshot to Allure: {e}", name="Error", attachment_type=allure.attachment_type.TEXT)