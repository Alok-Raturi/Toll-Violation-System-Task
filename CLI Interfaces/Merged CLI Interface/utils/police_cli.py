import logging
import requests
from email_validator import validate_email,EmailNotValidError
from utils.invalid_password import Invalid_Password
import re


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
    def __init__(self, URL,token):
        self.token = token
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


    def view_vehicle_challan(self, vehicle_number):
        try:
            response = requests.get(f"{self.BASE_URL}police/get-challans/{vehicle_number}", headers=self.get_headers())
            response.raise_for_status()
            return {"status": response.status_code, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": 500, "data": {response.json()}}

    def create_challan(self, vehicleId, amount, description, location):
        challan_data = {
            "vehicleId": vehicleId,
            "amount": int(amount),
            "description": description,
            "location": location
        }
        try:
            response = requests.post(self.BASE_URL + "police/create-challan", json=challan_data, headers=self.get_headers())
            response.raise_for_status()
            return {"status": response.status_code, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status": 500, "data": {response.json()}}

    def logout(self):
        self.token = None
