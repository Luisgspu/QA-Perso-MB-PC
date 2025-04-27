# filepath: d:\Python\QA App Personalization\QA-APP-GUI\QA With Image Verifier and Payload Print\TestSteps.py

import allure
import logging
from selenium.webdriver.support.ui import WebDriverWait

@allure.step("Navigate to HOME_PAGE: {url}")
def navigate_to_home_page(driver, url):
    driver.get(url)
    WebDriverWait(driver, 15).until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    logging.info(f"🌍 Navigated to: {url}")