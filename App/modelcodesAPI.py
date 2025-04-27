import requests
import logging

class ModelCodesAPI:
    def __init__(self, access_token):
        """
        Initializes the ModelCodesAPI class with an access token for making API requests.
        
        Args:
            access_token (str): The access token for the API.
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def fetch_model_codes(self, market_code):
        """
        Fetches and filters model codes for passenger cars from the API.

        Args:
            market_code (str): The market code to fetch model codes for.

        Returns:
            list: A list of passenger car model codes, or an empty list if an error occurs.
        """
        url = f"https://api.oneweb.mercedes-benz.com/vehicle-deeplinks-api/v1/deeplinks/{market_code}/model-series"
        try:
            # Realiza la solicitud GET
            response = requests.get(url, headers=self.headers)

            # Verifica si la solicitud fue exitosa
            if response.status_code == 200:
                # Parsear la respuesta JSON
                try:
                    data = response.json()
                    if not isinstance(data, dict):
                        logging.error("La respuesta de la API no tiene el formato esperado.")
                        return []

                    # Filtrar los modelos disponibles
                    passenger_car_model_codes = []
                    for model_key, model_data in data.items():
                        # Verificar si cualquier URL en el modelo contiene "/vans/", "/amg/" o "/maybach/"
                        contains_excluded_keywords = any(
                            keyword in value.get("modelSeriesUrl", "")
                            for key, value in model_data.items()
                            if isinstance(value, dict)
                            for keyword in ["/vans/", "/amg-gt-2-door/", "/amg-gt-4-door/", "/mercedes-maybach-s-class/", "/mercedes-maybach-sl/", "/maybach-eqs/", "/maybach/"]
                        )
                        # Si contiene alguna de las palabras clave excluidas, excluir el modelo
                        if not contains_excluded_keywords:
                            passenger_car_model_codes.append(model_key)
                    return passenger_car_model_codes
                except ValueError:
                    logging.error("Error al parsear la respuesta JSON.")
                    return []
            else:
                logging.error("Error al recuperar los datos. Código de estado: %s", response.status_code)
                return []
        except requests.exceptions.RequestException as e:
            logging.error("Ocurrió un error al realizar la solicitud: %s", e)
            return []

# Uso de la clase
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Reemplaza con tu token de acceso y código de mercado
    access_token = "YOUR_ACCESS_TOKEN"  # Reemplazar con el token de acceso real
    market_code = "IT/it"

    # Crear una instancia de la clase
    api = ModelCodesAPI(access_token)

    # Llamar al método para obtener los códigos de modelos
    passenger_car_model_codes = api.fetch_model_codes(market_code)

    if passenger_car_model_codes:
        print("Passenger Car Model Codes:", passenger_car_model_codes)
    else:
        print("No se encontraron códigos de modelos de autos de pasajeros o ocurrió un error.")