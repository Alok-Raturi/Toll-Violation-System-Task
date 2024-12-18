import email_validator as ev
import re
import requests
import json

PROMPT = """
PRESS 1 FOR CREATING A POLICE MAN
PRESS 2 FOR CREATING A TOLL PLAZA MAN
PRESS 3 FOR CREATING A VEHICLE
PRESS 4 FOR ISSUING A FASTAG
PRESS 5 FOR EXIT
"""

BASE_URL = "http://localhost:7071/api/rto/"

PASSWORD_REGEX = "^(?=.*[A-Z].*[A-Z])(?=.*[!@#$&*])(?=.*[0-9].*[0-9])(?=.*[a-z].*[a-z].*[a-z]).{8}$"

PASSWORD_CONSTRAINT = """
Your password:\n
    - should have 2 uppercase characters\n
    - should have 1 special character\n
    - should have 2 digits\n
    - should have 3 lowercase characters\n
    - should have minimum length of 8 characters
"""

# create-toll-plaza-man
# create-police-man
# create-vehicle
# create-fastag

def print_api_results(response):
    if response.get('status') == 200 or response.get('status') == 201:
        print(response.get('message'))
        print("Police created successfully")
    else:
        print(response.get('message'))
        print("Failed to create police")

class Rto_Officer:
    def __init__(self):
        pass

    def create_police(self,name,email,password):
        user_data = json.dumps({
            "name": name,
            "email": email,
            "password": password,
            "designation": "police"
        })
        created_police = requests.post(f"{BASE_URL}create-police-man",data=user_data)
        return {
            'status': created_police.status_code,
            'message': created_police
        }

    def create_toll_plaza(self,name,email,password):
        user_data = json.dumps({
            "name": name,
            "email": email,
            "password": password,
            "designation": "toll"
        })
        created_toll_plaza = requests.post(f"{BASE_URL}create-toll-plaza")
        return {
            'status': created_toll_plaza.status_code,
            'message': created_toll_plaza
        }

    def create_vehicle(self,vehicleid,email,name,designation,password):
        vehicle_data = json.dumps({
            "vehicleId": vehicleid,
            "email": email,
            "name": name,
            "designation": designation,
            "password": password
        })
        created_vehicle = requests.post(f"{BASE_URL}create-vehicle",data=vehicle_data)
        return {
            'status': created_vehicle.status_code,
            'message': created_vehicle
        }

    def issue_fastag(self,tagid,vehicleid):
        fastag_data = json.dumps({
            "tagId": tagid,
            "vehicleId": vehicleid
        })
        created_fastag = requests.post(f"{BASE_URL}create-fastag",data=fastag_data)
        return {
            'status': created_fastag.status_code,
            'message': created_fastag
        }


if __name__ =="__main__":
    print("Welcome to the RTO Application")
    print("Please select the option from the below menu")
    print(PROMPT)
    option = input("Enter the option: ")
    rto_officer = Rto_Officer()

    if option == "1" or option == "2":
        name = input("Enter the name: ")
        email = input("Enter the email: ")
        password = input("Enter the password: ")
        if not ev.validate_email(email):
            print("Invalid email entered")
            print("EXITING THE APPLICATION")

        if not re.match(PASSWORD_REGEX, password):
            print(PASSWORD_CONSTRAINT)
            print("EXITING THE APPLICATION")

        if option == "1":
            print("Creating a police")
            response = rto_officer.create_police(name,email,password)
            print_api_results(response)
        elif option == "2":
            print("Creating a toll plaza")
            response = rto_officer.create_toll_plaza(name,email,password)
            print_api_results(response)

    elif option == "3":
        print("Creating a vehicle")
        response = rto_officer.create_vehicle()
        print_api_results(response)

    elif option == "4":
        print("Issuing a fastag")
        response = rto_officer.issue_fastag()
        print_api_results(response)
    elif option == "5":
        print("Exiting the application")
        print("Thank you for using the application")
    else:
        print("Invalid option selected. EXITING THE APPLICATION............")