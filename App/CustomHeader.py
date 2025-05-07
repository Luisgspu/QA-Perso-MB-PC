import logging
from selenium import webdriver
from CreateDriver import build_chrome_options, create_driver

def test_custom_header():
    # Build options and create the driver
    options = build_chrome_options()
    driver = create_driver(options)

    try:
        # Log the test start
        logging.info("🌐 Starting test to verify custom header 'traffic_type: internal'.")

        # Navigate to a public HTTP header inspection service
        test_url = "https://webhook.site/e5b11a23-8cb9-4d67-9e33-04ba2e642107"
        logging.info(f"🌍 Navigating to: {test_url}")
        driver.get(test_url)

        # Wait for the page to load and fetch the page source
        page_source = driver.page_source

        # Log the page source for debugging
        logging.debug(f"🔍 Page source:\n{page_source}")

        # Check if the custom header is present in the response
        if "traffic_type" in page_source and "internal" in page_source:
            logging.info("✅ Custom header 'traffic_type: internal' is present in the request.")
        else:
            logging.error("❌ Custom header 'traffic_type: internal' is NOT present in the request.")
            logging.debug(f"🔍 Full page source:\n{page_source}")
    except Exception as e:
        logging.error(f"❌ Test failed with error: {e}")
    finally:
        driver.quit()

# Run the test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Set logging level to INFO
    test_custom_header()