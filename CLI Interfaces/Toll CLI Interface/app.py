import requests
import json

BASE_TOLL_URL = "http://localhost:7072/api/toll/"

INITIAL_PROMPT = "PRESS\n1 for LOGIN\n2 for EXIT\nEnter Your Choice: "
AFTER_LOGIN_PROMPT = "" 

print(INITIAL_PROMPT)

class TollPlazaPerson:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def login(self):
        auth_data = json.dumps({"email": self.email, "password": self.password})
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
            "data": response.json(),
            "status_code": response.status_code
        }

    def view_fastag_balance(self):
        response = requests.get(f"{BASE_TOLL_URL}get-balance/{tagId}", headers = {"Authorization": self.token})
        return {
            "data" : response.json(),
            "status_code": response.status_code
        }

    def vehicle_entry_at_toll(self):
        # settle overdue challans
        pass

def app_runner():
    pass

if __name__ == '__main__':
    pass