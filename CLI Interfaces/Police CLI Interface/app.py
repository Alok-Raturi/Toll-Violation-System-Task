import datetime
import logging
from utils.traffic_police import Traffic_Police
import getpass

TEST_BASE_URL = "http://localhost:7071/api/police/"
PROD_BASE_URL = "https://raturifunctionapp.azurewebsites.net/api/police/"

logging.basicConfig(filename='traffic_police.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def show_menu(menu_options):
    for option, description in menu_options.items():
        print(f"Press {option} for {description}")
    print("\n")
    return input("Enter your choice: ")

def validate_amount(amount):
    try:
        if not amount.isnumeric():
            print("\nInvalid Amount. Please enter a valid amount.\n")
            return None
        amount = float(amount)
        if amount <= 0:
            print("\nAmount must be greater than zero.\n")
            return None
        return amount
    except ValueError:
        print("\nInvalid amount. Please enter a valid number.\n")
        return None

if __name__ == '__main__':
    print("Press 1 for Login\nPress 2 for Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        username = input("Enter email: ").strip()
        password = str(getpass.getpass("Enter your password: "))
        traffic_police = Traffic_Police(username, password,PROD_BASE_URL)
        login_response = traffic_police.login()

        if login_response['status'] == 200:
            print("\n----------------- Login Successful ------------------------\n")
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
        else:
            print(login_response['body'])

    elif choice == '2':
        print("Exiting...")
    else:
        print("Invalid choice. Exiting...")

