# QA App Allure Testing

This project provides automated QA testing with detailed Allure reporting for web applications. It uses Python, Pytest, Selenium, and integrates with Allure for rich test result visualization.

## Installation

Use Poetry to install dependencies:
```bash
poetry install
```

## Usage

### Run Tests

To execute all tests and generate Allure results:
```bash
poetry run pytest QAAppAllure.py -n auto -s -v --reruns 4 --alluredir=report allure-results

```

### Generate Allure Report

After running tests, generate the Allure HTML report:
```bash
allure generate allure-results --clean -o allure-report
allure open allure-report
```

### Running in CI/CD

This project includes GitHub Actions workflows for scheduled and on-demand test execution. See `.github/workflows/` for examples.

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
├── test_dictionaries
│   ├── BFV1.json
│   ├── BFV2.json
│   ├── BFV3.json
│   ├── Last Seen SRP.json
│   ├── Last Seen PDP.json
│   ├── Last Configuration Started.json
│   └── Las Configuration Completed.json
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md

```

## Test Flow

The main test orchestration is handled in `QAAppAllure.py`. Here’s how the test flow works:

1. **Defining Test Cases**  
   - The `manual_test_cases` list in `QAAppAllure.py` defines which tests to run.
   - Each entry specifies a `test_name`, `market_code`, and optionally a `model_code`.
     - If `model_code` is provided: Only that specific model will be tested for the given market and test type.
     - If `model_code` is omitted or set to `None`: The test will run for **all available models** in the specified market for that test type.

2. **Fetching URLs and Building Test Cases**  
   - For each entry in `manual_test_cases`, the script calls the `VehicleAPI` to fetch all necessary URLs and metadata for the test.
     - If a `model_code` is specified, only URLs for that model are fetched.
     - If no `model_code` is specified, the API returns URLs for **all models** in that market, and a test case is created for each model.
   - The result is a combined list of test cases (`all_test_cases`) that includes both manually specified and dynamically generated cases.

3. **Test Execution**  
   - The test runner uses `pytest.mark.parametrize` to execute the `test_run` function for each test case in `all_test_cases`.
   - For each test case:
     1. The test context is set up (browser, context, page, XHR capturer, etc.).
     2. The appropriate test logic is selected based on `test_name` (e.g., BFV1, Last Configuration Started, etc.).
     3. The test navigates to the required URLs, performs actions, and validates personalization/campaign logic.
     4. Results and failures are reported to Allure.

4. **Allure Reporting**  
   - Each test case is reported in Allure with details such as market, model, test type, and any relevant tags.
   - If you specify a `model_code` in `manual_test_cases`, only that model is tested and reported.
   - If you omit `model_code`, **all models** for the given market and test type are tested and reported as separate suites in Allure.

### Example

```python
manual_test_cases = [
    {"test_name": "BFV1", "market_code": "DE/de", "model_code": "S214"},  # Only S214 model
    {"test_name": "Last Seen SRP", "market_code": "DE/de"},               # All models in DE/de
]
```
- The first entry will test only the S214 model for BFV1 in DE/de.
- The second entry will test **all models** for "Last Seen SRP" in DE/de.

## Running Tests

To run all tests in parallel with reruns and Allure reporting, use the following command:

```sh
pytest QAAppAllure.py -n 4 -s -v --reruns 4 --alluredir=allure-results
```

- `-n 4` runs tests in parallel using 4 CPU cores. Adjust this number based on your machine's available cores.
- `--reruns 4` will rerun any failed test up to 4 times.
- `--alluredir=allure-results` saves the results for Allure reporting.
- `-s` allows print/log output to be shown in the console.
- `-v` enables verbose output.

You can change the values for `-n` and `--reruns` depending on your hardware and reliability needs.

---

## Allure Reporting

After running your tests, you can generate and view the Allure report locally with the following commands (for example, if Allure is installed at `C:\Allure\allure-2.33.0\bin`):

```sh
C:\Allure\allure-2.33.0\bin\allure generate allure-results -o allure-report --clean
C:\Allure\allure-2.33.0\bin\allure serve allure-results
```

- The first command generates a static HTML report in the `allure-report` folder.
- The second command starts a local server to view the report in your browser.

Make sure to adjust the path if your Allure installation is in a different location.

## .gitignore

A recommended `.gitignore` for this project:

```
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.pyc

# Virtual environments
.env/
.venv/
env/
venv/

# Poetry
poetry.lock

# Allure results and reports
allure-results/
allure-report/

# Test outputs
*.log
*.tmp

# VS Code settings
.vscode/

# OS files
.DS_Store
Thumbs.db

# Other
*.swp
```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

# Other
*.swp
Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

License
This project is licensed under the MIT License. See the LICENSE file for details.
