import json
import logging
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium_stealth import stealth
import allure



class XHRResponseCapturer:
    """Captures XHR responses, filtering by Daimler's API."""
    
    def __init__(self, driver, target_url_filter, target_campaign_name_substring=""):
        self.driver = driver
        self.TARGET_URL_FILTER = target_url_filter
        self.TARGET_CAMPAIGN_NAME_SUBSTRING = target_campaign_name_substring
        self.setup_stealth()
        self.enable_network_logging()
        self.captured_data = []

    def setup_stealth(self):
        """Applies stealth settings to evade detection in headless mode."""
        with allure.step("Setting up stealth mode for the browser"):
            stealth(self.driver,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)

    def enable_network_logging(self):
        """Enables network tracking to capture response bodies."""
        with allure.step("Enabling network logging"):
            self.driver.execute_cdp_cmd("Network.enable", {"enableCors": True, "maxPostDataSize": 5000000})
        
    def set_campaign_name_substring(self, test_name):
        """Dynamically sets the campaign name substring based on the test name."""
        with allure.step(f"Setting campaign name substring for test: {test_name}"):
            if not test_name:
                allure.attach("Test name is empty or None. Defaulting to no filter.", name="Warning", attachment_type=allure.attachment_type.TEXT)
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = ""
                return

            if "Personalized CTA" in test_name:
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = "personalized cta"
            elif "Personalized CTA OWCC" in test_name:
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = "personalized cta"
            elif "BFV1" in test_name:
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = "best-fitting-vehicle"
            elif "BFV2" in test_name:
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = "best-fitting-vehicle"
            elif "BFV3" in test_name:
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = "best-fitting-vehicle"        
            elif "Last Configuration Started" in test_name:
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = "last-configuration"
            elif "Last Configuration Completed" in test_name:
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = "last-configuration"
            elif "Last Seen SRP" in test_name:
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = "dcp-last-seen-pdp-srp"
            elif "Last Seen PDP" in test_name:
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = "dcp-last-seen-pdp-srp"        
            else:
                self.TARGET_CAMPAIGN_NAME_SUBSTRING = ""  # Default to no filter
            allure.attach(f"Campaign name substring set to: {self.TARGET_CAMPAIGN_NAME_SUBSTRING}", name="Info", attachment_type=allure.attachment_type.TEXT)

    def process_browser_log_entry(self, entry):
        """Extracts relevant data from the browser log."""
        try:
            return json.loads(entry['message'])['message']
        except json.JSONDecodeError:
            return None

    def capture_responses(self):
        """Captures and filters XHR responses with status 200 and matching campaign names."""
        with allure.step("Capturing XHR responses"):
            browser_log = self.driver.get_log('performance')
            events = [self.process_browser_log_entry(entry) for entry in browser_log]
            events = [event for event in events if event and event.get('method') == 'Network.responseReceived']

            for event in events:
                request_id = event["params"]["requestId"]
                response = event["params"]["response"]
                response_url = response["url"]
                status = response["status"]

                # Skip 204 responses entirely
                if status == 204:
                    continue  # Ignore and move to the next response

                # Only continue if it's the desired endpoint and a successful (200) response
                if self.TARGET_URL_FILTER in response_url and status == 200:
                    try:
                        response_body = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                        response_text = response_body.get("body", "")

                        try:
                            json_response = json.loads(response_text)
                            if "campaignResponses" in json_response:
                                # Filter campaign responses based on the TARGET_CAMPAIGN_NAME_SUBSTRING
                                filtered_campaigns = [
                                    campaign for campaign in json_response["campaignResponses"]
                                    if self.TARGET_CAMPAIGN_NAME_SUBSTRING.lower() in campaign.get("campaignName", "").lower()
                                ]

                                # If there are matching campaigns, save the filtered response
                                if filtered_campaigns:
                                    filtered_response = {
                                        "url": response_url,
                                        "status": status,
                                        "body": {"campaignResponses": filtered_campaigns}
                                    }
                                    self.captured_data.append(filtered_response)

                                    # Attach filtered response to Allure for debugging
                                    formatted_response = json.dumps(filtered_response, indent=4, ensure_ascii=False)
                                    allure.attach(formatted_response, name=f"Filtered Campaign Response from {response_url}", attachment_type=allure.attachment_type.JSON)

                        except json.JSONDecodeError:
                            allure.attach(response_text, name=f"Raw Response Body from {response_url}", attachment_type=allure.attachment_type.TEXT)

                    except Exception as e:
                        logging.error(f"Error capturing response for {response_url}: {e}")
                elif self.TARGET_URL_FILTER in response_url:
                    allure.attach(f"Ignored response with status {status}: {response_url}", name="Info", attachment_type=allure.attachment_type.TEXT)
                
    def get_captured_data(self):
        """Returns the captured XHR responses."""
        return self.captured_data

    @staticmethod
    def attach_xhr_to_allure(xhr_path):
        """Attaches XHR data to Allure report."""
        try:
            with open(xhr_path, 'r', encoding='utf-8') as file:
                allure.attach(file.read(), name="XHR Responses", attachment_type=allure.attachment_type.JSON)
        except Exception as e:
            allure.attach(f"Error attaching XHR data to Allure: {e}", name="Error", attachment_type=allure.attachment_type.TEXT)