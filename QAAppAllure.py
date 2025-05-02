# Standard Library Imports
import unittest
import os
import time
import json
import logging
import sys
import pytest
import allure
import sys
import os
import hashlib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Third-Party Imports
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
import requests

# Local Module Imports
from App.vehicle_api import VehicleAPI  # Importing from the separate module
from App.modelcodesAPI import ModelCodesAPI
from App.ImageVerifier import ImageVerifier  # Importing from the separate module
from App.ScreenshotHandler import ScreenshotHandler  # Importing from the separate module
from App.XHRResponseCapturer import XHRResponseCapturer  # Importing from the separate module
from App.CookiesHandler import CookieHandler  # Importing from the separate module
from App.CTAHandlerDOM import CTAHandler  # Importing from the separate module
from App.CTAVerifier import CTAVerifier   # Importing from the separate module  
from App.CreateDriver import create_driver
from App.CreateDriver import restart_driver
from App.CreateDriver import build_chrome_options
from App.CreateAPIandXHR import create_api_and_xhr
from App.VerifyPersonalizationAndCapture import verify_personalization_and_capture
from TestsCodes import test_bfv1
from TestsCodes import test_bfv2
from TestsCodes import test_bfv3
from TestsCodes import test_LastConfigStarted
from TestsCodes import test_LastConfigCompleted
from TestsCodes import test_LastSeenSRP
from TestsCodes import test_LastSeenPDP
from TestsCodes import PersonalizedCTA1_test
from TestsCodes import PersonalizedCTA2_test
from TestsCodes import PersonalizedCTA3_test
from TestsCodes import PersonalizedCTA4_test


test_mapping = {
    "BFV1": test_bfv1.BFV1Test,
    "BFV2": test_bfv2.BFV2Test,
    "BFV3": test_bfv3.BFV3Test,
    "Last Configuration Started": test_LastConfigStarted.LCStartedTest,
    "Last Configuration Completed": test_LastConfigCompleted.LCCompletedTest,
    "Last Seen SRP": test_LastSeenSRP.LSeenSRPTest,
    "Last Seen PDP": test_LastSeenPDP.LSeenPDPTest,
    "Personalized CTA 1": PersonalizedCTA1_test.PersonalizedCTA1Test,
    "Personalized CTA 2": PersonalizedCTA2_test.PersonalizedCTA2Test,
    "Personalized CTA 3": PersonalizedCTA3_test.PersonalizedCTA3Test,
    "Personalized CTA 4": PersonalizedCTA4_test.PersonalizedCTA4Test,
    # Agrega más aquí si tienes otros
}

# Función para adjuntar capturas de pantalla a Allure
def attach_screenshot_to_allure(screenshot_path):
    try:
        logging.info(f"📸 Attaching screenshot to Allure: {screenshot_path}")
        with open(screenshot_path, 'rb') as file:
            allure.attach(file.read(), name="Screenshot", attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        logging.error(f"❌ Error attaching screenshot to Allure: {e}")


def attach_xhr_to_allure(xhr_path):
    try:
        logging.info(f"📁 Attaching XHR responses to Allure: {xhr_path}")
        with open(xhr_path, 'r', encoding='utf-8') as file:
            allure.attach(file.read(), name="XHR Responses", attachment_type=allure.attachment_type.JSON)
    except Exception as e:
        logging.error(f"❌ Error attaching XHR data to Allure: {e}")



# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

TARGET_URL_FILTER = "https://daimleragemea.germany-2.evergage.com/"



@pytest.fixture(scope="function")
def screenshot_dir():
    screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests")
    os.makedirs(screenshot_dir, exist_ok=True)
    return screenshot_dir


def run_test(driver, test_name, market_code, model_code, model_name, body_type, attempt, urls, api_and_xhr, screenshot_dir):
    vehicle_api, xhr_capturer = api_and_xhr
    test_success = False

    if not urls or 'HOME_PAGE' not in urls or not urls['HOME_PAGE']:
        allure.attach(f"❌ Could not fetch valid URLs for test '{test_name}' (market: {market_code}, model: {model_code})")
        pytest.fail(f"Missing HOME_PAGE URL for test '{test_name}'")

    allure.step(f"🌐 Fetched URLs from API for test '{test_name}':\n"
                f"Model Name: {urls.get('MODEL_NAME', 'N/A')}\n"
                f"Body Type: {urls.get('BODY_TYPE', 'N/A')}\n"
                f"URLs:\n{json.dumps(urls, indent=2)}")

    # BFV Logic
    if 'CONFIGURATOR' not in urls or not urls['CONFIGURATOR']:
        if test_name in ["BFV1", "BFV2", "BFV3", "Last Configuration Started", "Last Configuration Completed"]:
            message = f"❌ Skipping test '{test_name}' due to lack of CONFIGURATOR URL."
            logging.warning(message)
            allure.dynamic.description(message)
            pytest.skip(message)

    if 'ONLINE_SHOP' not in urls or not urls['ONLINE_SHOP']:
        if test_name in ["BFV2", "BFV3", "Last Seen PDP", "Last Seen SRP"]:
            message = f"❌ Skipping test '{test_name}' due to lack of ONLINE_SHOP URL."
            logging.warning(message)
            allure.dynamic.description(message)
            pytest.skip(message)

    if 'TEST_DRIVE' not in urls or not urls['TEST_DRIVE']:
        if test_name == "BFV3":
            message = f"❌ Skipping test '{test_name}' due to lack of TEST_DRIVE URL."
            logging.warning(message)
            allure.dynamic.description(message)
            pytest.skip(message)

    try:
        driver.get(urls['HOME_PAGE'])
        WebDriverWait(driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
        logging.info(f"🌍 Navigated to: {urls['HOME_PAGE']}")
    except Exception as e:
        logging.error(f"❌ Error navigating to HOME_PAGE: {e}")
        pytest.fail(f"Error navigating to HOME_PAGE: {e}")

    try:
        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "cmm-cookie-banner"))
        )
        time.sleep(2)
        logging.info("✅ Cookie banner detected.")
        driver.execute_script("""
            document.querySelector("cmm-cookie-banner").shadowRoot.querySelector("wb7-button.button--accept-all").click();
        """)
        allure.step("✅ Clicked on accept cookies.")
    except Exception as ex:
        allure.attach("❌ Cookie banner not found or already accepted.")

    # Execute test
    if test_name in test_mapping:
        test_instance = test_mapping[test_name](driver, urls)
        test_instance.run()
        allure.step(f"✅ {test_name} test completed.")
        time.sleep(4)

        test_success = verify_personalization_and_capture(
            driver, test_name, model_name, body_type, attempt, screenshot_dir,
            test_success, xhr_capturer, urls
        )

    if not test_success:
        failure_message = f"❌ Test '{test_name}' failed."
        logging.error(failure_message)
        allure.attach(failure_message, name="Test Failure", attachment_type=allure.attachment_type.TEXT)
        pytest.fail(failure_message)



# Manually defined test cases
manual_test_cases = [
    
    
   
    
    {
        "test_name": "BFV1",
        "market_code": "AT/de",
        "model_code": "W465"
    },
    
     {
        "test_name": "BFV1",
        "market_code": "AT/de",
        "model_code": "C236"
    },
    
    
  
    
    

    

    

    
    

    
    
    
    
    
    
    
    
]

# Fetch dynamic test cases for manual model codes
dynamic_test_cases = []
vehicle_api = VehicleAPI("YOUR_ACCESS_TOKEN")  # Replace with your actual access token

for manual_case in manual_test_cases:
    market_code = manual_case["market_code"]
    test_name = manual_case["test_name"]
    model_code = manual_case.get("model_code", None)  # Get model_code, default to None if not provided

    # Fetch URLs for the specific model code or all models if model_code is not provided
    fetched_cases = vehicle_api.fetch_models_for_market(market_code, test_name, model_code=model_code)
    if fetched_cases:
        if model_code:
            # Update the manual case with the fetched URLs for the specific model
            manual_case["urls"] = fetched_cases[0].get("urls", {})
            manual_case["model_name"] = fetched_cases[0].get("model_name", None)
            manual_case["body_type"] = fetched_cases[0].get("body_type", None)
        else:
            # Add all fetched cases to dynamic_test_cases if no model_code is provided
            dynamic_test_cases.extend(fetched_cases)
    else:
        logging.warning(f"⚠️ No URLs found for manual case: {manual_case}")

# Combine manual and dynamic test cases
all_test_cases = manual_test_cases + dynamic_test_cases

@pytest.mark.parametrize("test_case", all_test_cases)
def test_run(test_case, screenshot_dir):
    """
    Runs a test for each test case, either manually defined or dynamically fetched.
    """
    test_name = test_case['test_name']
    market_code = test_case.get('market_code', 'BE/nl')
    model_code = test_case.get('model_code', None)
    model_name = test_case.get('model_name', None)
    body_type = test_case.get('body_type', None)
    urls = test_case.get('urls', {})

    # Log test case details
    logging.info(f"Running test case: {json.dumps(test_case, indent=2)}")

    # Validate URLs
    if not urls or 'HOME_PAGE' not in urls or not urls['HOME_PAGE']:
        logging.error(f"❌ Missing HOME_PAGE URL for test '{test_name}' (market: {market_code}, model: {model_code}).")
        allure.attach(f"❌ Missing HOME_PAGE URL for test '{test_name}' (market: {market_code}, model: {model_code}).")
        return
    
    
    # Generar ID único y consistente para Allure
    uid_raw = f"{test_name}_{market_code}_{model_code or 'unknown'}"
    uid_hashed = hashlib.md5(uid_raw.encode()).hexdigest()
    allure.dynamic.id(uid_hashed)

    # Define browser options and create driver
    options = build_chrome_options()
    driver = create_driver(options)

    try:
        # Set Allure suite hierarchy
        allure.dynamic.parent_suite(f"{market_code}")  # Parent Suite
        allure.dynamic.suite(f"{test_name}")  # Suite
        allure.dynamic.sub_suite(f"{model_code or 'N/A'} - {model_name or 'N/A'} ({body_type or 'N/A'})")  # Sub-Suite

        # Add dynamic tags
        allure.dynamic.tag(test_name)
        allure.dynamic.tag(market_code)
        if model_code:
            allure.dynamic.tag(model_code)
        if body_type:
            allure.dynamic.tag(body_type)
        if model_name:
            allure.dynamic.tag(model_name)

        # Attach URLs to Allure
        allure.attach(
            json.dumps(urls, indent=2),
            name=f"URLs for {model_name or 'N/A'} ({body_type or 'N/A'})",
            attachment_type=allure.attachment_type.JSON
        )

        # Extract base test name
        base_test_name = test_name.split(" - ")[0]

        # Run the test logic for the current model
        try:
            api_and_xhr = create_api_and_xhr(driver)
            if api_and_xhr is None or api_and_xhr[1] is None:
                logging.error("❌ Failed to initialize API and XHR capturer.")
                allure.attach("❌ Failed to initialize API and XHR capturer.", name="Initialization Error", attachment_type=allure.attachment_type.TEXT)
                return
            if base_test_name in test_mapping:
                run_test(driver, base_test_name, market_code, model_code, model_name, body_type, 1, urls, api_and_xhr, screenshot_dir)
            else:
                raise ValueError(f"❌ Test logic for '{test_name}' is not defined in test_mapping.")
        except Exception as e:
            logging.error(f"❌ Test failed for model: {model_name or 'N/A'} ({body_type or 'N/A'}). Error: {e}")
            allure.attach(
                f"Error: {str(e)}",
                name=f"Error for {model_name or 'N/A'} ({body_type or 'N/A'})",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
    finally:
        driver.quit()
        logging.info("✅ Driver closed after test.")