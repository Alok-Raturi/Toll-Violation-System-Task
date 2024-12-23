import requests
import json
import time
import sys
import os

BASE_TOLL_URL = "https://raturifunctionapp.azurewebsites.net/api/toll/"

APP_INTRODUCTION = "\n-----------------  TOLL VIOLATION DETECTION SYSTEM  -----------------"
TOLL_INTRO = "\n-----------------  You are at Toll Plaza Person Portal  -----------------"
INITIAL_PROMPT = "\nPRESS \n1 for LOGIN\n2 for EXIT\n"
AFTER_LOGIN_PROMPT = """
\nPRESS
1 to view unsettled overdue challans of a vehicle
2 to fetch remaining balance of a FASTag
3 to make an entry of a vehicle at Toll Plaza
4 to Logout\n"""

def clear_console(): 
    if os.name == 'nt': 
        os.system('cls')
    else:
        os.system('clear')

def typewriter(text, delay=0.05):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

class TollPlazaPerson:
    def login(self, email, password):
        auth_data = json.dumps({"email": email, "password": password})
        response = requests.post(BASE_TOLL_URL + "login", data = auth_data)
        if(response.status_code == 200):
            self.token = response.json()['access_token']
        return {
            "body": response.json(),
            "status_code": response.status_code
        }
    
    def logout(self):
        self.email = None
        self.password = None
        self.token = None

    def view_challans(self, vehicle_id):
        response = requests.get(f"{BASE_TOLL_URL}get-challan/{vehicle_id}", headers = {"Authorization": self.token})
        return {
            "body": response.json(),
            "status_code": response.status_code
        }

    def view_fastag_balance(self, tag_id):
        response = requests.get(f"{BASE_TOLL_URL}get-balance/{tag_id}", headers = {"Authorization": self.token})
        return {
            "body" : response.json(),
            "status_code": response.status_code
        }

    def vehicle_entry_at_toll(self, vehicle_id, passage_amount):
        toll_data = {
            "passage-amount": passage_amount
        }
        response = requests.post(f"{BASE_TOLL_URL}settle-overdue-challans/{vehicle_id}", json = toll_data, headers = {"Authorization": self.token})
        return {
            "body" : response.json(),
            "status_code": response.status_code
        }

def app_runner():
    clear_console()
    print('\n')
    print(APP_INTRODUCTION)
    print(TOLL_INTRO)
    typewriter(INITIAL_PROMPT)
    user_choice = input("Enter Your Choice: ")
    while user_choice != '2':
        if user_choice == '1':
            # Login
            print("\n-----------------  LOGIN  -----------------\n")
            user_email = input("Enter registered email: ").strip()
            user_password = input("Enter password: ").strip()
            # Using dummy values for testing purposes
            toll_user = TollPlazaPerson()
            login = toll_user.login(user_email, user_password)

            if login['status_code'] == 200:
                # Login successful
                clear_console()
                print("\n-----------------  LOGIN SUCCESSFUL  -----------------")
                typewriter(AFTER_LOGIN_PROMPT, delay=0.01)
                login_choice = input("Enter your choice: ")
                while login_choice != '4':
                    if login_choice == '1':
                        print("\n-----------------  VIEW UNSETTLED OVERDUE CHALLANS  -----------------")
                        vehicle_id = input("\nEnter Vehicle ID: ") 
                        response = toll_user.view_challans(vehicle_id)
                        if response['status_code'] == 200:
                            print(response['body'])
                        else:
                            print(response['body'])  
                        print()
                        typewriter(AFTER_LOGIN_PROMPT, delay=0.01) 
                        login_choice = input("Enter your choice: ")     
                    elif login_choice == '2':    
                        print("\n-----------------  VIEW REMAINING BALANCE  -----------------")
                        tag_id = input("\nEnter FASTag ID: ")
                        response = toll_user.view_fastag_balance(tag_id)
                        if response['status_code'] == 200:
                            print(response['body'])
                        else:
                            print(response['body'])
                        # print()
                        typewriter(AFTER_LOGIN_PROMPT, delay=0.01) 
                        login_choice = input("Enter your choice: ")    
                    elif login_choice == '3':
                        print("\n-----------------  NEW ENTRY OF A VEHICLE  -----------------")
                        vehicle_id = input("\nEnter Vehicle ID: ") 
                        passage_amount = input("Enter Passage Amount for Vehicle: ")

                        while not passage_amount.isnumeric():
                            passage_amount = input("\nEnter valid Passage Amount: ")

                        response = toll_user.vehicle_entry_at_toll(vehicle_id, passage_amount)
                        if response['status_code'] == 200:
                            print(response['body'])
                        else:
                            print(response['body'])
                        
                        print()
                        typewriter(AFTER_LOGIN_PROMPT, delay=0.01) 
                        login_choice = input("Enter your choice: ")
                    elif login_choice == '4':
                        print("Logging you out ...")
                        time.sleep(1)
                        toll_user.logout()
                        print("\n-----------------  Logout Successful  -----------------\n")
                    else:
                        print("Invalid Choice !  ABORTING")
                        login_choice = input("Enter your choice again: ")
            else:
                print('\n')
                print(login['body'])

        elif user_choice == '2':
            print("\nExiting from application\n")
        else:
            print('Invalid choice')
            typewriter(INITIAL_PROMPT)
            user_choice = input('Enter your choice: ')


if __name__ == '__main__':
    app_runner()