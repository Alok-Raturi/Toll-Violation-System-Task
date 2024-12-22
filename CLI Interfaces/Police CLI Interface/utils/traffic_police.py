import logging
import requests
from email_validator import validate_email,EmailNotValidError
from utils.invalid_password import Invalid_Password
import re

logger = logging.getLogger()

PASSWORD_REGEX = "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?=\S+$).{8,20}$"

PASSWORD_CONSTRAINT = """
Your password:\n
    - should have at least 1 uppercase characters\n
    - should have at least 1 special character - ?=.*[@#$%^&+=]\n
    - should have at least 1 digits\n
    - should have at least 1 lowercase characters\n
    - should not contain any whitespace characters\n
    - should have minimum length of 8 characters and max length of 20 characters
"""

class Traffic_Police:
    def __init__(self, email, password,URL):
        self.email = email
        self.password = password
        self.token = None
        self.BASE_URL = URL

    def get_headers(self):
        return {"Authorization": self.token} if self.token else {}

    def validate_credentials(self):
        try:
            validate_email(self.email)
            if not re.match(PASSWORD_REGEX,self.password):
                raise Invalid_Password("Password do not match required constraints.")
        except EmailNotValidError:
            raise EmailNotValidError

    def login(self):
        auth_data = {"email": self.email, "password": self.password}
        try:
            self.validate_credentials()
            response = requests.post(self.BASE_URL + "login", json=auth_data)
            response.raise_for_status() 
            self.token = response.json()['access_token']
            logger.info(f"User {self.email} logged in successfully.")
            return {"status": response.status_code, "body": response.json()}
        except EmailNotValidError as e:
            logger.error(f"Login failed, Invalid email {self.email}")
            return {"status": 500, "body": "Invalid Email"}
        except Invalid_Password as e:
            logger.error(f"Password do not match the required credentials for email : {self.email}")
            return {"status":500,"body":PASSWORD_CONSTRAINT}
        except requests.exceptions.RequestException as e:
            logger.error(f"Login failed for {self.email}: {response.json()}")
            return {"status": 500, "body": response.json()}

    def view_vehicle_challan(self, vehicle_number):
        try:
            response = requests.get(f"{self.BASE_URL}get-challan/{vehicle_number}", headers=self.get_headers())
            response.raise_for_status()
            return {"status": response.status_code, "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve challan for vehicle {vehicle_number}: {response.json()}")
            return {"status": 500, "data": {response.json()}}

    def create_challan(self, vehicleId, amount, description, location):
        challan_data = {
            "vehicleId": vehicleId,
            "amount": int(amount),
            "description": description,
            "location": location
        }
        try:
            response = requests.post(self.BASE_URL + "create-challan", json=challan_data, headers=self.get_headers())
            response.raise_for_status()
            logger.info(f"Challan created successfully for vehicle {vehicleId} with amount {amount}.")
            return {"status": response.status_code, "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create challan for vehicle {vehicleId}: {response.json()}")
            return {"status": 500, "data": {response.json()}}

    def logout(self):
        logger.info(f"User {self.email} logged out.")
        self.email = None
        self.password = None
        self.token = None
