import logging
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CookieHandler:
    """Handles cookie banners across different websites."""

    def __init__(self, driver):
        self.driver = driver

    @allure.step("Accept cookies if the cookie banner is present")
    def accept_cookies(self):
        """Handles the cookie banner and accepts cookies if present."""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "cmm-cookie-banner"))
            )
            logging.info("✅ Cookie banner detected.")
            self.driver.execute_script("""
                document.querySelector("cmm-cookie-banner").shadowRoot.querySelector("wb7-button.button--accept-all").click();
            """)
            logging.info("✅ Clicked on accept cookies.")
            allure.attach("Cookie banner accepted", name="Cookie Handling", attachment_type=allure.attachment_type.TEXT)
        except Exception as ex:
            logging.error(f"❌ Cookie banner not found or could not click: {ex}")
            allure.attach(str(ex), name="Error Details", attachment_type=allure.attachment_type.TEXT)
            raise

# Pytest Test Case
@pytest.fixture
def cookie_handler(driver):
    """Fixture to initialize the CookieHandler."""
    return CookieHandler(driver)

@pytest.mark.usefixtures("driver")
@allure.feature("Cookie Handling")
@allure.story("Test Cookie Banner Acceptance")
def test_accept_cookies(cookie_handler):
    """Test case to verify cookie banner acceptance."""
    with allure.step("Attempt to accept cookies"):
        cookie_handler.accept_cookies()