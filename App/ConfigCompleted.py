import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

class ConfiguratorCompleted:
    def __init__(self, driver):
        """Initializes the Configurator with a WebDriver instance."""
        self.driver = driver

    def expand_shadow_element(self, shadow_host):
        """Expands a shadow DOM element."""
        shadow_root = self.driver.execute_script(
            "return arguments[0].shadowRoot", shadow_host)
        return shadow_root

    def perform_configurator_actions(self):
        """Performs the necessary actions in the configurator."""
        try:
            # Locate the shadow host and expand the shadow root
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, 'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owcc-car-configurator')
            shadow_root = self.expand_shadow_element(shadow_host)

            # Locate the main frame element inside the shadow DOM
            main_frame = shadow_root.find_element(By.CSS_SELECTOR, '#cc-app-container-main > div.cc-app-container__main-frame.cc-grid-container > div.cc-app-container__navigation.ng-star-inserted > cc-navigation > nav > div > ul')
            
            # Hover over the main frame
            actions = ActionChains(self.driver)
            actions.move_to_element(main_frame).perform()
            logging.info('✅ Hovered over the main frame (ul element).')

            # Click on the main frame
            main_frame.click()
            logging.info('✅ Clicked on the main frame (ul element).')
            time.sleep(3)

            # Locate and click the last child element inside the main frame
            last_child = shadow_root.find_element(By.CSS_SELECTOR, '#cc-app-container-main > div.cc-app-container__main-frame.cc-grid-container > div.cc-app-container__navigation.ng-star-inserted > cc-navigation > nav > div > ul > li:last-child')
            
            # Hover over the last child
            actions.move_to_element(last_child).perform()
            logging.info('✅ Hovered over the last child element (li:last-child).')

            # Click on the last child
            last_child.click()
            logging.info('✅ Clicked on the last child element (li:last-child).')
            time.sleep(3)

        except Exception as e:
            logging.error(f"❌ Error in configurator: {e}")
                
            