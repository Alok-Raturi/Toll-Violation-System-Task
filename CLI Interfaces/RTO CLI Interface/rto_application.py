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

# create-toll-plaza-man
# create-police-man
# create-vehicle
# create-fastag

def print_api_results(response):
    if response.get('status') == 200 or response.get('status') == 201:
        print(f"\n{response.get('message')}\n")
    else:
        print(f"\n{response.get('message')}\n")

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
        print("\nYour request is processing...........\n")
        created_police = requests.post(f"{BASE_URL}create-police-man",data=user_data)
        return {
            'status': created_police.status_code,
            'message': created_police.json()
        }

    def create_toll_plaza(self,name,email,password):
        user_data = json.dumps({
            "name": name,
            "email": email,
            "password": password,
            "designation": "toll"
        })
        print("\nYour request is processing...........\n")
        created_toll_plaza = requests.post(f"{BASE_URL}create-toll-plaza-man",data=user_data)
        return {
            'status': created_toll_plaza.status_code,
            'message': created_toll_plaza.json()
        }

    def create_vehicle(self,vehicleid,email,name,password):
        vehicle_data = json.dumps({
            "vehicleId": vehicleid,
            "email": email,
            "name": name,
            "designation": "user",
            "password": password
        })
        print("\nYour request is processing...........\n")
        created_vehicle = requests.post(f"{BASE_URL}create-vehicle",data=vehicle_data)
        return {
            'status': created_vehicle.status_code,
            'message': created_vehicle.json()
        }

    def issue_fastag(self,tagid,vehicleid):
        fastag_data = json.dumps({
            "tagId": tagid,
            "vehicleId": vehicleid
        })
        print("\nYour request is processing...........\n")
        created_fastag = requests.post(f"{BASE_URL}create-fastag",data=fastag_data)
        return {
            'status': created_fastag.status_code,
            'message': created_fastag.json()
        }


if __name__ =="__main__":
    print("Welcome to the RTO Application")
    rto_officer = Rto_Officer()
    while True:
        print("Please select the option from the below menu")
        print(PROMPT)
        option = input("Enter the option: ")

        if option == "1" or option == "2":
            name = input("Enter the name: ")
            email = input("Enter the email: ")
            password = input("Enter the password: ")
            if not ev.validate_email(email):
                print("Invalid email entered")

            if not re.match(PASSWORD_REGEX, password):
                print("Your password does not meet the following constraints")
                print(PASSWORD_CONSTRAINT)

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
            vehicleid = input("Enter the vehicle id: ")
            email = input("Enter the email: ")
            name = input("Enter the name: ")
            password = input("Enter the password: ")
            if not re.match(PASSWORD_REGEX, password):
                print("Your password does not meet the following constraints")
                print(PASSWORD_CONSTRAINT)
            

            response = rto_officer.create_vehicle(vehicleid,email,name,password)
            print_api_results(response)

        elif option == "4":
            print("Issuing a fastag")
            tagid = input("Enter the tag id: ")
            vehicleid = input("Enter the vehicle id: ")
            response = rto_officer.issue_fastag(tagid,vehicleid)
            print_api_results(response)
            
        elif option == "5":
            print("Exiting the application")
            print("Thank you for using the application")
            del rto_officer
            break
        else:
            print("Retry .......")