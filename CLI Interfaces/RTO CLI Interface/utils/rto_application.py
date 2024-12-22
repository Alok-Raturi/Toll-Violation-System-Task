import logging
import requests
from utils.validations import validate_email_input,validate_password

logger = logging.getLogger()

class Rto_Officer:
    def __init__(self,BASE_URL):
        self.BASE_URL = BASE_URL

    def create_user(self, designation, name, email, password):
        if not validate_email_input(email):
            return
        if not validate_password(password):
            return 

        user_data = {
            "name": name,
            "email": email,
            "password": password,
            "designation": designation
        }
        designation = 'toll-plaza' if designation=='toll' else 'police'
        response = self.handle_api_request(f"create-{designation}-man", user_data)
        logger.info(f"User created: {name} with designation {designation}")
        return response

    def create_vehicle(self, vehicleid, email, name, password):
        if not validate_email_input(email):
            return
        if not validate_password(password):
            return

        vehicle_data = {
            "vehicleId": vehicleid,
            "email": email,
            "name": name,
            "designation": "user",
            "password": password
        }
        response = self.handle_api_request("create-vehicle", vehicle_data)
        logger.info(f"Vehicle created with ID: {vehicleid}")
        return response

    def issue_fastag(self, tagid, vehicleid):
        fastag_data = {
            "tagId": tagid,
            "vehicleId": vehicleid
        }
        response = self.handle_api_request("create-fastag", fastag_data)
        logger.info(f"Fastag issued with ID: {tagid} for vehicle ID: {vehicleid}")
        return response

    def handle_api_request(self,endpoint, data):
        try:
            logger.info(f"Sending request to {endpoint} with data: {data}")
            print("\nYour request is processing...........\n")
            response = requests.post(f"{self.BASE_URL}{endpoint}", json=data)
            response.raise_for_status()
            return {"status": response.status_code, "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            return {'status': 500, 'data': response.json()}