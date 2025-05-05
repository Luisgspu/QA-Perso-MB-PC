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
        time.sleep(4)
        self.handle_cookies()
        time.sleep(2)
        
        try:
            # Localizar el shadow host
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, parent_selector)
            logging.info("✅ Shadow host located successfully.")

            shadow_root = self.expand_shadow_element(shadow_host)
            logging.info("✅ Shadow root expanded successfully.")

            # Buscar 'cc-navigation'
            nav_element = shadow_root.find_element(By.CSS_SELECTOR, 'cc-navigation')
            nav_element.click()
            time.sleep(2)  # Espera opcional para cualquier acción
            if not nav_element:
                raise Exception("❌ 'cc-navigation' no encontrado.")

            nested_shadow = self.expand_shadow_element(nav_element)

            if nested_shadow:
                logging.info("✅ Nested shadow DOM encontrado.")
                main_frame = nested_shadow.find_element(By.CSS_SELECTOR, 'nav > div > ul')
            else:
                logging.info("ℹ️ No nested shadow DOM. Usando nav_element directamente.")
                nav_inside = nav_element.find_element(By.CSS_SELECTOR, 'nav')
                if not nav_inside:
                    raise Exception("❌ No se encontró <nav> dentro de cc-navigation.")
                main_frame = nav_inside.find_element(By.CSS_SELECTOR, 'div > ul')

            if not main_frame:
                raise Exception("❌ No se encontró el main frame <ul>.")

            logging.info("✅ Main frame (ul element) localizado correctamente.")

            # Espera a que haya al menos un <li>
            WebDriverWait(self.driver, 10).until(
                lambda d: len(main_frame.find_elements(By.CSS_SELECTOR, 'li')) > 0
            )

            child_elements = main_frame.find_elements(By.CSS_SELECTOR, 'li')
            logging.info(f"✅ {len(child_elements)} child elements encontrados dentro del ul.")
            logging.debug(f"🔍 HTML de main_frame:\n{main_frame.get_attribute('outerHTML')}")

            # Click al último elemento
            last_child = child_elements[-1]
            logging.info("🔍 HTML del último <li>:\n%s", last_child.get_attribute("outerHTML"))

            # Desplaza y pasa el mouse por encima
            self.driver.execute_script("arguments[0].scrollIntoView(true);", last_child)
            ActionChains(self.driver).move_to_element(last_child).perform()
            time.sleep(1)

            try:
                # Intenta encontrar un <a> o <button> dentro del <li>
                link_inside = last_child.find_element(By.CSS_SELECTOR, 'a, button')
                logging.info("✅ Elemento interno (<a>/<button>) encontrado en el <li>.")
                logging.info("🔍 HTML del clickable interno:\n%s", link_inside.get_attribute("outerHTML"))

                # Intenta hacer clic con JS
                self.driver.execute_script("arguments[0].click();", link_inside)
                logging.info("✅ Click en elemento interno del último <li> (a/button).")

            except Exception as inner_click_err:
                logging.warning(f"⚠️ No se encontró un <a> o <button> dentro del último <li>: {inner_click_err}")
                logging.info("ℹ️ Intentando clic directo sobre el <li> con JS.")

                try:
                    self.driver.execute_script("arguments[0].click();", last_child)
                    logging.info("✅ Click forzado en último <li> usando JS.")
                except Exception as fallback_err:
                    logging.error(f"❌ No se pudo hacer click en el <li> ni en sus hijos: {fallback_err}")
            
            time.sleep(3)  # Espera opcional para cualquier acción
          

        except Exception as e:
            logging.error(f"❌ Error durante la verificación de elementos: {e}")
        
        

    def test_verify_elements(self):
        url = "https://www.mercedes-benz.it/passengercars/mercedes-benz-cars/car-configurator.html/motorization/CCci/IT/it/EQE-KLASSE/OFFROADER"
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