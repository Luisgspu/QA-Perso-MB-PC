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
        """Performs the necessary actions in the configurator."""
        try:
            # Find shadow host and expand it
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, 
                'body > div.root.responsivegrid.owc-content-container > div > div.responsivegrid.ng-content-root.aem-GridColumn.aem-GridColumn--default--12 > div > owcc-car-configurator')
            shadow_root = self.expand_shadow_element(shadow_host)

            # Locate the main frame element inside the shadow DOM
            main_frame = shadow_root.find_element(By.CSS_SELECTOR, 
                '#cc-app-container-main > div.cc-app-container__main-frame.cc-grid-container > div.cc-app-container__navigation.ng-star-inserted > cc-navigation > nav > div > ul > li:nth-child(3) > ccwb-text > a')

            # Perform actions: hover over and click the main frame
            actions = ActionChains(self.driver)
            actions.move_to_element(main_frame).perform()
            logging.info('✅ Hovered over Navigation main frame')

            main_frame.click()
            logging.info('✅ Clicked on Navigation main frame')

            # Sleep for 5 seconds to let any page load or action settle
            time.sleep(5)
        except Exception as e:
            logging.error(f"❌ Error in configurator: {e}")
