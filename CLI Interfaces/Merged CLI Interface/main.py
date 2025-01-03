import getpass
import json
import requests
from jose import JWTError, jwt
import datetime
from utils.toll_cli import TollPlazaPerson
from utils.police_cli import Traffic_Police


PROD_BASE_TOLL_URL = "https://raturifunctionapp.azurewebsites.net/api/"
TEST_BASE_TOLL_URL = "http://localhost:7071/api/"
ACCESS_TOKEN = ""
ALGORITHM = "RS256"

def get_public_key(token:str):
    header = jwt.get_unverified_headers(token)
    kid = header['kid']
    print(header)
    payload = jwt.get_unverified_claims(token)
    print(payload)
    
    url = payload['url']
    response = requests.get(url).json()
    public_key = [item for item in response if item['kid'] == kid]
    return public_key[0]['public-key']

def decode_token(token:str):
    try:
        public_key = f'''{get_public_key(token)}'''
        return jwt.decode(token, public_key, algorithms=[ALGORITHM])
    except JWTError:
        raise JWTError("Error decoding token")

APP_INTRODUCTION = "\n-----------------  TOLL VIOLATION DETECTION SYSTEM  -----------------"
# TOLL_INTRO = "\n-----------------  You are at Toll Plaza Person Portal  -----------------"
INITIAL_PROMPT = "\nPRESS \n1 for LOGIN\n2 for EXIT\n"
AFTER_LOGIN_PROMPT = """
\nPRESS
1. View unsettled overdue challans
2. Fetch remaining balance
3. Scan Vehicle
4. Logout\n"""

def login( email, password):
    auth_data = json.dumps({"email": email, "password": password})
    response = requests.post(TEST_BASE_TOLL_URL + "login", data = auth_data)
    return {
        "body": response.json(),
        "status_code": response.status_code
    }

def show_menu(menu_options):
    for option, description in menu_options.items():
        print(f"Press {option} for {description}")
    print("\n")
    return input("Enter your choice: ")

def validate_amount(amount):
    # try:
        if not amount.isnumeric():
            print("\nInvalid Amount. Please enter a valid amount.\n")
            return False
        return amount
    # except ValueError:
    #     print("\nInvalid amount. Please enter a valid number.\n")
    #     return False

def TollPlaza(toll_user):
    while True:
        print(AFTER_LOGIN_PROMPT)
        login_choice = input("Enter your choice: ").strip()
        if login_choice == '1':
            print("\n-----------------  VIEW UNSETTLED OVERDUE CHALLANS  -----------------")
            vehicle_id = input("\nEnter Vehicle ID: ") 
            response = toll_user.view_challans(vehicle_id)
            if response['status_code'] == 200:
                challan_list = response['body']
                print('''
    ID\t\t\t\t\tAmount\t\tLocation\tDescription\t\tDate\t\tDue Time
                        ''')
                for challan in challan_list:
                    due_time = datetime.datetime.fromtimestamp(challan['due_time'])
                    formatted_due_time = due_time.strftime('%Y-%m-%d %H:%M:%S')
                    print(f'''
    {challan['id']}\t{challan['amount']}\t\t{challan['location']}\t{challan['description']}\t{challan['date']}\t{formatted_due_time}
                    ''')
            else:
                print('\n',response['body'])  
            continue
        elif login_choice == '2':    
            print("\n-----------------  VIEW REMAINING BALANCE  -----------------")
            tag_id = input("\nEnter FASTag ID: ")
            response = toll_user.view_fastag_balance(tag_id)
            if response['status_code'] == 200:
                print("Remaining Balance: ",response['body'])
            else:
                print('\n', response['body'])
            continue
        elif login_choice == '3':
            print("\n-----------------  SCAN VEHICLE  -----------------")
            vehicle_id = input("\nEnter Vehicle ID: ") 
            toll_location = input("Enter toll plaza's location: ")
            passage_amount = input("Enter Passage Amount for Vehicle: ").strip()

            while not passage_amount.isnumeric():
                passage_amount = input("\nEnter valid Passage Amount: ").strip()

            response = toll_user.vehicle_entry_at_toll(vehicle_id, passage_amount, toll_location)
            if response['status_code'] == 200:
                print(response['body'])
            else:
                print('\n', response['body'])
            continue
        elif login_choice == '4':
            print("Logging you out ...")
            toll_user.logout()
            print("\n-----------------  Logout Successful  -----------------\n")
            break
        else:
            print("Invalid Choice!")
            # login_choice = input("Enter your choice again: ").strip()


def PoliceUser(traffic_police):
    while True:
        menu = {
            '1': 'Creating a Challan',
            '2': 'Viewing Challan of a Vehicle',
            '3': 'Logout'
        }
        choice = show_menu(menu)
        print()
        if choice == '1':
            vehicle_id = input("Enter vehicle number: ")
            amount = input("Enter amount: ")
            vehicle_id= vehicle_id.upper()

            amount = validate_amount(amount)
            if amount is None:
                continue
            description = input("Enter description: ")
            location = input("Enter location: ")
            response = traffic_police.create_challan(vehicle_id, amount, description, location)
            if response['status'] in [200, 201]:
                print("\nChallan created successfully!\n")
            else:
                print(f"\nError: {response['data']}\n")

        elif choice == '2':
            vehicle_id = input("Enter vehicle number: ")
            vehicle_id = vehicle_id.upper()
            response = traffic_police.view_vehicle_challan(vehicle_id)
            if response['status'] == 200:
                challan_list = response['data']
                print("---------------------- All Challans ------------------")
                print('''
ID\t\t\t\t\tAmount\t\tLocation\t  Status\tDescription\t\tDate\t\tDue Time
                        ''')
                for challan in challan_list:
                    due_time = datetime.datetime.fromtimestamp(challan['due_time'])
                    formatted_due_time = due_time.strftime('%Y-%m-%d %H:%M:%S')
                    print(f'''
{challan['id']}\t{challan['amount']}\t\t{challan['location']}\t{challan['status']}\t{challan['description']}\t{challan['date']}\t{formatted_due_time}
                    ''')
            else:
                print(f"Error: {response['data']}")

        elif choice == '3':
            print("Logging you out...")
            traffic_police.logout()
            del traffic_police
            break
        else:
            print("Invalid choice. Please try again.")

def main_app():
    print(APP_INTRODUCTION)
    print(INITIAL_PROMPT)

    choice = input("Enter your choice: ")
    if choice == '1':
        email = input("Enter your email: ").strip()
        password = getpass.getpass()
        response = login(email,password)
        if response["status_code"] == 200:
            ACCESS_TOKEN = response["body"]["access_token"]
            response = decode_token(ACCESS_TOKEN)
            if response['designation'] == 'police':
                traffic_police = Traffic_Police(TEST_BASE_TOLL_URL,ACCESS_TOKEN)
                print("\n---------- Logged in as Police ----------\n")
                PoliceUser(traffic_police)
            elif response['designation'] == 'toll':
                toll_user = TollPlazaPerson(TEST_BASE_TOLL_URL,ACCESS_TOKEN)
                print("\n---------- Logged in as Toll Plaza Person ----------\n")
                TollPlaza(toll_user)
            else:
                print("Invalid designation")
                print("Exiting your applicatio....")
        else:
            print("Your credentials are not valid. ")
            print("Exiting your program")         

    elif choice == '2':
        # exit
        print("Exiting your program.....")
    else:
        print("Invalid option...")
        print("Exiting your program")

if __name__ == '__main__':
    main_app()


