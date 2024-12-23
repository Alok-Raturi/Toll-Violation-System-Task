import logging
import getpass
from utils.rto_application import Rto_Officer

PROMPT = """
PRESS 1 FOR CREATING A POLICE MAN
PRESS 2 FOR CREATING A TOLL PLAZA MAN
PRESS 3 FOR CREATING A VEHICLE
PRESS 4 FOR ISSUING A FASTAG
PRESS 5 FOR EXIT
"""

logging.basicConfig(filename='rto_application.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

PROD_BASE_URL = "https://raturifunctionapp.azurewebsites.net/api/rto/"
TEST_BASE_URL = "http://localhost:7071/api/rto/"


def print_api_results(response):
    if response.get('status') in [200, 201]:
        logger.info(f"Request successful: {response.get('data')}")
        print(f"\n{response.get('data')}\n")
    else:
        logger.error(f"Request failed: {response.get('data')}")
        print(f"\n{response.get('data')}\n")

def get_input_for_user_creation():
    name = input("Enter the name: ")
    email = input("Enter the email: ")
    password = getpass.getpass("Enter your password: ")
    logger.info(f"User input received for creation: {name}, {email}")
    return name, email, password


def get_input_for_vehicle_creation():
    vehicleid = input("Enter the vehicle id: ")
    name,email,password = get_input_for_user_creation()
    logger.info(f"User input received for vehicle creation: {vehicleid}, {email}")
    return vehicleid, email, name, password


def get_input_for_fastag_issuing():
    tagid = input("Enter the tag id: ")
    vehicleid = input("Enter the vehicle id: ")
    logger.info(f"User input received for fastag issuing: {tagid}, {vehicleid}")
    return tagid, vehicleid


if __name__ == "__main__":
    logger.info("RTO Application started.")
    print("Welcome to the RTO Application")
    rto_officer = Rto_Officer(BASE_URL=PROD_BASE_URL)
    while True:
        print("Please select the option from the below menu")
        print(PROMPT)
        option = input("Enter the option: ")
        logger.info(f"User selected option {option}")
        
        if option == "1" or option == "2":
            name, email, password = get_input_for_user_creation()
            usertype = "police" if option=="1" else "toll"
            print(f"Creating a {usertype} man\n")
            response = rto_officer.create_user(usertype, name, email, password)
            if response:
                print_api_results(response)

        elif option == "3":
            print("Creating a vehicle")
            vehicleid, email, name, password = get_input_for_vehicle_creation()
            response = rto_officer.create_vehicle(vehicleid, email, name, password)
            if response:
                print_api_results(response)

        elif option == "4":
            print("Issuing a fastag")
            tagid, vehicleid = get_input_for_fastag_issuing()
            response = rto_officer.issue_fastag(tagid, vehicleid)
            print_api_results(response)

        elif option == "5":
            logger.info("Exiting the application.")
            print("Exiting.....\nThank you for using the application")
            del rto_officer
            break

        else:
            logger.warning("Invalid option selected.")
            print("Retry .......")
