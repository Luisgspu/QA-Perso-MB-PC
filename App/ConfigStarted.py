import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

class ConfiguratorStarted:
    def __init__(self, driver):
        """Initializes the Configurator with a WebDriver instance."""
        self.driver = driver

    def expand_shadow_element(self, shadow_host):
        """Expands a shadow DOM element."""
        shadow_root = self.driver.execute_script(
            "return arguments[0].shadowRoot", shadow_host)
        return shadow_root

    def perform_configurator_actions(self):
        """Performs navigation and clicks inside the car configurator menu."""
        try:
            logging.info("🔍 Starting configurator interaction.")

            # Locate shadow host and expand root
            shadow_host = self.driver.find_element(By.CSS_SELECTOR,
                'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owcc-car-configurator')
            shadow_root = self.expand_shadow_element(shadow_host)
            logging.info("✅ Shadow DOM expanded.")

            # Access main <ul> inside navigation
            main_frame = shadow_root.find_element(By.CSS_SELECTOR,
                '#cc-app-container-main > div.cc-app-container__main-frame.cc-grid-container > div.cc-app-container__navigation.ng-star-inserted > cc-navigation > nav > div > ul')
            ActionChains(self.driver).move_to_element(main_frame).perform()
            logging.info("✅ Hovered over the main frame (ul element).")
            main_frame.click()
            logging.info("✅ Clicked on the main frame (ul element).")
            time.sleep(2)

            # Find the last <li> in the nav
            second_child = shadow_root.find_element(By.CSS_SELECTOR,
                '#cc-app-container-main > div.cc-app-container__main-frame.cc-grid-container > div.cc-app-container__navigation.ng-star-inserted > cc-navigation > nav > div > ul > li:nth-child(2)')
            logging.info("🔍 Found last child element (li:last-child).")

            # Hover over it
            ActionChains(self.driver).move_to_element(second_child).perform()
            logging.info("✅ Hovered over the last child element.")

            try:
                # Try to click a child <a> or <button> within the <li>
                link_inside = second_child.find_element(By.CSS_SELECTOR, 'a, button')
                self.driver.execute_script("arguments[0].click();", link_inside)
                logging.info("✅ Clicked on inner clickable element (a/button).")
            except:
                # Fallback: click the <li> itself
                self.driver.execute_script("arguments[0].click();", second_child)
                logging.info("✅ Fallback click on <li> using JavaScript.")

            time.sleep(2)

        except Exception as e:
            logging.error(f"❌ Error while performing configurator actions: {e}")