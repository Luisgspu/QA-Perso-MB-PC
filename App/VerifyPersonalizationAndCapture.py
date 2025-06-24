import json
import logging
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
from App.ScreenshotHandler import ScreenshotHandler
from App.CTAVerifierPDP import CTAVerifier
import pytest
from App.ImageVerifier import ImageVerifier

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


def verify_personalization_and_capture(
        driver, test_name, model_name, body_type, retries, screenshot_dir,
        test_success, xhr_capturer, urls):
    """
    Verifies the personalized image and captures XHR responses and screenshots.
    """
    try:
        # Check userGroup before verifying the personalized image
        with allure.step("🔍 Checking userGroup in XHR responses..."):
            try:
                if driver.session_id:
                    logging.info(f"ℹ️ Setting campaign name substring to: {test_name}")
                    xhr_capturer.set_campaign_name_substring(test_name)
                    logging.info("✅ Campaign name substring set successfully.")
                    
                    # Capture XHR responses
                    xhr_capturer.capture_responses()
                    xhr_data = xhr_capturer.get_captured_data()
                    logging.info(f"ℹ️ Captured XHR data: {xhr_data}")
                    
                    # Check userGroup for each campaign response
                    for response in xhr_data:
                        campaigns = response.get("body", {}).get("campaignResponses", [])
                        for campaign in campaigns:
                            campaign_name = campaign.get("campaignName", "Unknown Campaign")
                            user_group = campaign.get("userGroup", "Unknown UserGroup")
                            experience_Name = campaign.get("experienceName", "Unknown Experience")
                            
                            # Check if experienceName contains "Control Group" or userGroup is "control"
                            if "Control Group" in experience_Name or user_group.lower() == "control":  
                                with allure.step(f"❌ Campaign '{campaign_name}' is in the Control Group. Retrying test."):
                                    message = f"❌ Test '{test_name}' failed because the campaign was identified as part of the Control Group."
                                    pytest.fail(message)
                                    logging.info(f"ℹ️ Campaign '{campaign_name}' is in the Control Group. Retrying test without marking success or failure.")
                                
                                # Add a custom defect category for Control Group Fail
                                allure.dynamic.label("defect", "Control Group Fail")
                                allure.dynamic.tag("Control Group Issue")
                                
                                # Reset retries to ensure the next attempt is still the same number
                                retries -= 1
                                return False  # Retry the test without marking success or failure
                            else:
                                with allure.step(f"✅ Campaign '{campaign_name}' has userGroup: {user_group} and experienceName: {experience_Name}."):
                                    logging.info(f"✅ Campaign '{campaign_name}' has userGroup: {user_group} and experienceName: {experience_Name}.")
                else:
                    logging.warning("⚠️ WebDriver session is not active. Skipping XHR response capture.")
            except Exception as e:
                logging.error(f"❌ Failed to check userGroup in XHR responses: {e}")
                allure.attach(f"❌ Failed to check userGroup in XHR responses: {e}", name="XHR Error", attachment_type=allure.attachment_type.TEXT)
                retries -= 1  # Reset retries in case of an error
                return False  # Retry the test in case of an error

        # Verify the personalized image
        with allure.step("🔍 Verifying personalized image..."):
            try:
                # Determine the expected src based on the test_name
                if test_name in ["BFV1", "BFV2", "BFV3"]:
                    expected_src = "/content/dam/hq/personalization/campaignmodule/"
                else:
                    expected_src = "/images/dynamic/europe/"

                # Dynamically determine the selector based on the market
                selector = "[data-component-name='hp-campaigns']"
                
                # Wait for at least one image inside the selector to be present and loaded
                with allure.step("⏳ Waiting for images inside the campaign section to load..."):
                    try:
                        WebDriverWait(driver, 10).until(
                            lambda d: d.execute_script("""
                                const imgs = document.querySelectorAll(arguments[0] + ' img');
                                return Array.from(imgs).length > 0 && Array.from(imgs).every(img => img.complete && img.naturalHeight !== 0);
                            """, selector)
                        )
                        logging.info(f"✅ All images inside {selector} are loaded.")
                    except Exception as e:
                        logging.error(f"❌ Images inside {selector} did not load in time: {e}")
                        allure.attach(f"Error: {e}", name="Image Load Error", attachment_type=allure.attachment_type.TEXT)
                        return False

                # Scroll to the element
                with allure.step("📜 Scrolling to the element..."):
                    try:
                        element_to_scroll = driver.find_element(By.CSS_SELECTOR, selector)
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element_to_scroll)
                        logging.info(f"✅ Scrolled to element: {selector}")
                    except Exception as e:
                        logging.error(f"❌ Failed to scroll to element: {selector}. Error: {e}")
                        allure.attach(f"Error: {e}", name="Scroll Error", attachment_type=allure.attachment_type.TEXT)
                        return False

                # Capture screenshot
                time.sleep(1)  # Wait for the scroll to complete
                logging.info("📸 Taking screenshot...")
                screenshot_handler = ScreenshotHandler(driver, screenshot_dir)
                screenshot_path = os.path.join(screenshot_dir, f"{test_name}_attempt_{retries + 1}.png")

                try:
                    screenshot_handler.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)
                    logging.info(f"✅ Screenshot saved at: {screenshot_path}")

                    # Attach the screenshot to the Allure report
                    attach_screenshot_to_allure(screenshot_path)
                except Exception as e:
                    logging.error(f"❌ Failed to capture or attach screenshot: {e}")
                    
                # Verify the personalized image
                image_verifier = ImageVerifier(driver)
                test_success = image_verifier.verify_image(
                    selector=selector + " img",
                    expected_path=expected_src,
                    test_name=test_name,
                    timeout=6
                )
                
                
                test_success = True

                # Check if the current page is the last seen PDP
                if test_name == "Last Seen PDP":  # Adjust the condition based on your PDP URL structure
                    with allure.step("🔍 Verifying CTAs on the PDP"):
                        # Instantiate the CTAVerifierPDP class
                        cta_verifier = CTAVerifier(driver)

                        # Define selectors and expected href
                        parent_selector = 'div.hp-campaigns__content'
                        primary_cta_selector = 'div.hp-campaigns__content a'
                        
                        # Set the expected href value based on the market
                        if ".co.uk" in urls['HOME_PAGE']:
                            expected_href_value = "/buy/new-vans/product.html/"
                        else:
                            expected_href_value = "/buy/new-car/product.html/"

                        # Call the verify_ctas method
                        cta_verifier.verify_ctas(parent_selector, primary_cta_selector, expected_href_value)
                            
            except Exception as e:
                # Capture screenshot
                logging.info("📸 Taking screenshot...")
                time.sleep(1)  # Wait for the scroll to complete
                screenshot_handler = ScreenshotHandler(driver, screenshot_dir)
                screenshot_path = os.path.join(screenshot_dir, f"{test_name}_attempt_{retries + 1}.png")

                try:
                    screenshot_handler.scroll_and_capture_screenshot(urls, test_name, model_name, body_type, retries, test_success)
                    logging.info(f"✅ Screenshot saved at: {screenshot_path}")

                    # Attach the screenshot to the Allure report
                    attach_screenshot_to_allure(screenshot_path)
                except Exception as e:
                    logging.error(f"❌ Failed to capture or attach screenshot: {e}")
                    
        return test_success            
    
    except Exception as e:
        logging.error(f"❌ Error in verify_personalization_and_capture: {e}")
        allure.attach(f"❌ Error in verify_personalization_and_capture: {e}", name="Verify Personalization Error", attachment_type=allure.attachment_type.TEXT)
        return False