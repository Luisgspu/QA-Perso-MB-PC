# QA App Perso MB PC

This project is for automated QA testing with Allure reporting.

## Installation

Use Poetry to install dependencies:
```bash
poetry install
```

## Usage

### Run Tests

To execute all tests and generate Allure results:
```bash
poetry run pytest QAAppAllure.py --alluredir=allure-results
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
QA-App-Perso-MB-PC
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
├── QAAppAllure.py
├── requirements.txt
├── pytest.ini
└── .gitignore
```

## Customization

- **Add test cases:** Edit files in `TestsCodes/` or `App/` to add or modify test cases.
- **Configure Allure:** Adjust Allure steps and attachments in your test code for richer reporting.

## Troubleshooting

- **No space left on device:** Clean up old artifacts and temporary files in your CI environment.
- **Allure not generating reports:** Ensure you use the `--alluredir=allure-results` option with pytest and have Allure CLI installed.

## License

MIT License

---
