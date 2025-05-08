import pytest
import allure
import requests
import logging
from App.modelcodesAPI import ModelCodesAPI  # Importing from the separate module

class VehicleAPI:
    def __init__(self, access_token):
        """Initializes the VehicleAPI class with an access token for making API requests."""
        self.access_token = access_token
        self.model_codes_api = ModelCodesAPI(access_token)  # Initialize ModelCodesAPI

    @allure.step("Fetch URLs from API for market code '{market_code}' and model code '{model_code}'")
    def fetch_urls_from_api(self, market_code, model_code=None):
        """
        Fetches and processes URLs related to the vehicle model from the API.
        """
        if not model_code:
            logging.info(f"Fetching all model codes for market code '{market_code}'...")
            model_codes = self.model_codes_api.fetch_model_codes(market_code)
            if not model_codes:
                logging.error(f"No model codes found for market code '{market_code}'.")
                return []
        else:
            model_codes = [model_code]

        all_urls = []

        for code in model_codes:
            url = f"https://api.oneweb.mercedes-benz.com/vehicle-deeplinks-api/v1/deeplinks/{market_code}/model-series/{code}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                product_page = data.get('PRODUCT_PAGE', {}).get('url', '')
                configurator_url = data.get('CONFIGURATOR', {}).get('url', '')
                online_shop = data.get('ONLINE_SHOP', {}).get('url', '')
                test_drive = data.get('TEST_DRIVE', {}).get('url', '')
                home_page = self.construct_home_page_url(market_code, product_page, configurator_url)
                body_type, model_name = self.extract_body_type_and_model_name(product_page, market_code)

                logging.info(f"✅ Successfully fetched URLs for model code '{code}'.")
                all_urls.append({
                    'MODEL_CODE': code,  # Ensure model_code is included
                    'PRODUCT_PAGE': product_page,
                    'CONFIGURATOR': configurator_url,
                    'ONLINE_SHOP': online_shop,
                    'TEST_DRIVE': test_drive,
                    'HOME_PAGE': home_page,
                    'BODY_TYPE': body_type,
                    'MODEL_NAME': model_name
                })
            else:
                logging.error(f"❌ Failed to fetch URLs for model code '{code}'. Status code: {response.status_code}")

        return all_urls

    def fetch_models_for_market(self, market_code, test_name, model_code=None):
        """
        Fetches models for the given market code and returns a list of test cases.
        """
        vehicle_api = VehicleAPI("YOUR_ACCESS_TOKEN")  # Replace with your actual access token
        urls_list = vehicle_api.fetch_urls_from_api(market_code, model_code)

        test_cases = []
        for urls in urls_list:
            model_name = urls.get("MODEL_NAME", None)
            body_type = urls.get("BODY_TYPE", None)
            model_code = urls.get("MODEL_CODE", None)  # Extract model_code from the URLs
            

            if model_name and body_type:
                test_cases.append({
                    "test_name": test_name,
                    "market_code": market_code,
                    "model_code": model_code,
                    "model_name": model_name,
                    "body_type": body_type,
                    "urls": urls
                })
            else:
                logging.warning(f"⚠️ Skipping model due to missing MODEL_NAME or BODY_TYPE: {urls}")

        return test_cases        
            
    def construct_home_page_url(self, market_code, product_page, configurator_url):
        """Constructs the HOME_PAGE URL based on market code and the product/configurator URLs."""
        try:
            parts = product_page.split('/')
            if market_code.startswith("BE/nl_BE"):
                home_page = f"{parts[0]}//{parts[2]}/nl_BE"
            elif market_code.startswith("BE/fr"):
                home_page = f"{parts[0]}//{parts[2]}/fr"
            elif market_code.startswith("CH/de"):
                home_page = f"{parts[0]}//{parts[2]}/de"
            elif market_code.startswith("CH/it"):
                home_page = f"{parts[0]}//{parts[2]}/it"
            elif market_code.startswith("CH/fr"):
                home_page = f"{parts[0]}//{parts[2]}/fr"
            elif market_code.startswith("LU/de"):
                home_page = f"{parts[0]}//{parts[2]}/de"
            elif market_code.startswith("LU/fr"):
                home_page = f"{parts[0]}//{parts[2]}/fr"                                
            elif "/vans/" in configurator_url:
                home_page = f"{parts[0]}//{parts[2]}/vans"
            else:
                home_page = f"{parts[0]}//{parts[2]}/"

            # Log and attach constructed HOME_PAGE URL
            logging.info(f"✅ Constructed HOME_PAGE URL: {home_page}")
            return home_page
        except IndexError:
            logging.error("❌ Error constructing HOME_PAGE URL.")
            allure.attach("Error constructing HOME_PAGE URL", name="Error Details", attachment_type=allure.attachment_type.TEXT)
            pytest.fail("❌ Error: The CONFIGURATOR URL does not have the expected structure.")

    def extract_body_type_and_model_name(self, product_page, market_code):
        """Extracts the body type and model name from the PRODUCT_PAGE URL."""
        try:
            model_parts = product_page.split('/')
            specific_market_codes = ["LU/de", "LU/fr", "BE/nl_BE", "BE/fr", "CH/it", "CH/de", "CH/fr"]
            if any(market_code.startswith(code) for code in specific_market_codes):
                body_type = model_parts[6].upper()
                model_name = model_parts[7].upper()
            else:
                body_type = model_parts[5].upper()
                model_name = model_parts[6].upper()

            # Log and attach extracted data
            logging.info(f"✅ Extracted Body Type: {body_type}, Model Name: {model_name}")
            return body_type, model_name
        except IndexError:
            logging.error("❌ Error extracting body type and model name.")
            allure.attach("Error extracting body type and model name", name="Error Details", attachment_type=allure.attachment_type.TEXT)
            pytest.fail("❌ Error: The PRODUCT_PAGE URL does not have the expected structure.")
    
    
            
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Replace with your actual access token and market code
    access_token = "YOUR_ACCESS_TOKEN"
    market_code = "CH/it"
    model_code = "C174"  # Replace with a specific model code if needed, e.g., "X123"

    # Initialize VehicleAPI
    vehicle_api = VehicleAPI(access_token)

    if model_code:
        # Fetch URLs for the specific model
        logging.info(f"Fetching data for specific model code: {model_code}")
        specific_model_urls = vehicle_api.fetch_urls_from_api(market_code, model_code)

        if specific_model_urls:
            print(f"Model Code: {specific_model_urls[0]['MODEL_CODE']}")
            print(f"Product Page: {specific_model_urls[0]['PRODUCT_PAGE']}")
            print(f"Configurator: {specific_model_urls[0]['CONFIGURATOR']}")
            print(f"Online Shop: {specific_model_urls[0]['ONLINE_SHOP']}")
            print(f"Test Drive: {specific_model_urls[0]['TEST_DRIVE']}")
            print(f"Home Page: {specific_model_urls[0]['HOME_PAGE']}")
            print(f"Body Type: {specific_model_urls[0]['BODY_TYPE']}")
            print(f"Model Name: {specific_model_urls[0]['MODEL_NAME']}")
        else:
            print(f"No data found for model code: {model_code}")
    else:
        # Fetch URLs for all models in the market
        logging.info(f"Fetching data for all models in market code: {market_code}")
        all_model_urls = vehicle_api.fetch_urls_from_api(market_code)

        # Fetch models and generate test cases
        test_name = "BFV1"  # Replace with the appropriate test name
        test_cases = vehicle_api.fetch_models_for_market(market_code, test_name)    

        # Print the generated test cases
        print("\nGenerated Test Cases:")
        for test_case in test_cases:
            print(test_case)

        if all_model_urls:
            print("\nFetched URLs for All Models:")
            for model in all_model_urls:
                print(f"Model Code: {model['MODEL_CODE']}")
                print(f"Product Page: {model['PRODUCT_PAGE']}")
                print(f"Configurator: {model['CONFIGURATOR']}")
                print(f"Online Shop: {model['ONLINE_SHOP']}")
                print(f"Test Drive: {model['TEST_DRIVE']}")
                print(f"Home Page: {model['HOME_PAGE']}")
                print(f"Body Type: {model['BODY_TYPE']}")
                print(f"Model Name: {model['MODEL_NAME']}")
                print("-" * 50)
        else:
            print("No URLs found or an error occurred.")