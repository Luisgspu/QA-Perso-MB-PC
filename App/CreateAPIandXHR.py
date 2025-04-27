# 🔁 IMPORTS (si no están en este archivo)
from App.vehicle_api import VehicleAPI
from App.XHRResponseCapturer import XHRResponseCapturer # Si esto está en otro archivo
# TARGET_URL_FILTER debe estar definido globalmente o pasar como argumento

TARGET_URL_FILTER = "https://daimleragemea.germany-2.evergage.com/"

def create_api_and_xhr(driver):
    access_token = "your_api_access_token"
    vehicle_api = VehicleAPI(access_token)
    xhr_capturer = XHRResponseCapturer(driver, TARGET_URL_FILTER, "")
    return vehicle_api, xhr_capturer