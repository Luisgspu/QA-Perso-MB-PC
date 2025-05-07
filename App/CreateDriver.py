from selenium import webdriver
import logging
import pytest
import time


def build_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new") # Use new headless mode for better performance  
    options.add_argument("--disable-gpu") 
    options.add_argument("--enable-webgl")
    options.add_argument("--incognito")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--maximize")
    options.add_argument("--start-fullscreen")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    # Capabilities
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    options.set_capability("acceptInsecureCerts", True)

    return options


def create_driver(options):
    driver = webdriver.Chrome(options=options)
    driver.options = options  # Guardamos las opciones para reusarlas en el restart

    
    driver.fullscreen_window()
    return driver


def restart_driver(old_driver):
    try:
        options = old_driver.options  # usamos las opciones guardadas previamente
        old_driver.quit()
    except Exception as e:
        logging.warning(f"⚠️ Failed to quit the old browser: {e}")
        options = build_chrome_options()  # fallback en caso de fallo
    return create_driver(options)

@pytest.fixture
def driver():
    """Pytest fixture to initialize and clean up the WebDriver."""
    options = build_chrome_options()
    driver = create_driver(options)
    yield driver