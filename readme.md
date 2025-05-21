# QA Allure Reporting

This project is for QA testing with Allure reporting.

## Installation

# QA-App-Allure-Testing

## Overview
This project is designed for automated testing of web applications using Selenium and pytest. It includes various modules for handling screenshots, XHR responses, cookies, and API interactions, as well as a suite of test cases that validate different functionalities of the application.

## Project Structure
```
QA-App-Allure-Testing
├── App
│   ├── ScreenshotHandler.py
│   ├── XHRResponseCapturer.py
│   ├── CookiesHandler.py
│   ├── CTAHandlerDOM.py
│   ├── CTAVerifier.py
│   ├── CreateDriver.py
│   ├── CreateAPIandXHR.py
│   ├── VerifyPersonalizationAndCapture.py
│   ├── vehicle_api.py
│   ├── modelcodesAPI.py
│   └── ImageVerifier.py
├── TestsCodes
│   ├── test_bfv1.py
│   ├── test_bfv2.py
│   ├── test_bfv3.py
│   ├── test_LastConfigStarted.py
│   ├── test_LastConfigCompleted.py
│   ├── test_LastSeenSRP.py
│   ├── test_LastSeenPDP.py
│   ├── PersonalizedCTA1_test.py
│   ├── PersonalizedCTA2_test.py
│   ├── PersonalizedCTA3_test.py
│   └── PersonalizedCTA4_test.py
├── playwright
│   ├── browser_setup.py
│   ├── page_objects
│   │   ├── home_page.py
│   │   ├── configurator_page.py
│   │   └── test_drive_page.py
│   └── utils
│       ├── api_handler.py
│       ├── screenshot_handler.py
│       └── xhr_handler.py
├── tests
│   ├── test_bfv1_playwright.py
│   ├── test_bfv2_playwright.py
│   ├── test_bfv3_playwright.py
│   ├── test_LastConfigStarted_playwright.py
│   ├── test_LastConfigCompleted_playwright.py
│   ├── test_LastSeenSRP_playwright.py
│   ├── test_LastSeenPDP_playwright.py
│   ├── PersonalizedCTA1_test_playwright.py
│   ├── PersonalizedCTA2_test_playwright.py
│   ├── PersonalizedCTA3_test_playwright.py
│   └── PersonalizedCTA4_test_playwright.py
├── requirements.txt
├── pytest.ini
└── .gitignore
```

## Setup Instructions
1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd QA-App-Allure-Testing
   ```

2. **Install dependencies**:
   Ensure you have Python installed, then run:
   ```
   pip install -r requirements.txt
   ```

3. **Install Playwright Browsers**:
   After installing Playwright, you need to install the necessary browsers:
   ```
   playwright install
   ```

## Running Tests
To run the tests, use the following command:
```
pytest
```

You can also run specific tests by specifying the test file:
```
pytest tests/test_bfv1_playwright.py
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
