import datetime
import logging
from utils.traffic_police import Traffic_Police
import getpass

BASE_URL = "http://localhost:7071/api/police/"

logging.basicConfig(filename='traffic_police.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def show_menu(menu_options):
    """Display menu options and get user input."""
    for option, description in menu_options.items():
        print(f"Press {option} for {description}")
    return input("Enter your choice: ")

def validate_amount(amount):
    """Validate if the amount entered is a valid number."""
    try:
        if amount.isnumeric():
            print("Invalid Amount. Please enter a valid amount.")
            return None
        amount = float(amount)
        if amount <= 0:
            print("Amount must be greater than zero.")
            return None
        return amount
    except ValueError:
        print("Invalid amount. Please enter a valid number.")
        return None

if __name__ == '__main__':
    print("Press 1 for Login\nPress 2 for Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        username = input("Enter email: ").strip()
        password = getpass.getpass()
        traffic_police = Traffic_Police(username, password,BASE_URL)
        login_response = traffic_police.login()

        if login_response['status'] == 200:
            print("Login Successful")
            while True:
                menu = {
                    '1': 'Creating a Challan',
                    '2': 'Viewing Challan of a Vehicle',
                    '3': 'Logout'
                }
                choice = show_menu(menu)

                if choice == '1':
                    vehicle_id = input("Enter vehicle number: ")
                    amount = input("Enter amount: ")
                    amount = validate_amount(amount)
                    if amount is None:
                        continue
                    description = input("Enter description: ")
                    location = input("Enter location: ")
                    response = traffic_police.create_challan(vehicle_id, amount, description, location)
                    if response['status'] in [200, 201]:
                        print("Challan created successfully!")
                    else:
                        print(f"Error: {response['data']}")

                elif choice == '2':
                    vehicle_id = input("Enter vehicle number: ")
                    response = traffic_police.view_vehicle_challan(vehicle_id)
                    if response['status'] == 200:
                        challan_list = response['data']
                        print("---------------------- All Challans ------------------")
                        print('''
                              ID\t\t\t\t
                              Amount\t
                              Location\t\t
                              Status\t\t
                              Description\t
                              Date\t\t
                              Due Time''')
                        for challan in challan_list:
                            due_time = datetime.datetime.fromtimestamp(challan['due_time'])
                            formatted_due_time = due_time.strftime('%Y-%m-%d %H:%M:%S')
                            print(f'''
                                {challan['id']}\t
                                {challan['amount']}\t
                                {challan['location']}\t
                                {challan['status']}\t
                                {challan['description']}\t
                                {challan['date']}\t
                                {formatted_due_time}''')
                    else:
                        print(f"Error: {response['data']}")

                elif choice == '3':
                    print("Logging you out...")
                    traffic_police.logout()
                    break
                else:
                    print("Invalid choice. Please try again.")
        else:
            print(login_response['body'])

    elif choice == '2':
        print("Exiting...")
    else:
        print("Invalid choice. Exiting...")

