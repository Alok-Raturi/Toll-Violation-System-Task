import requests
import json

class TollPlazaPerson:
    def __init__(self,BASE_URL,token):
        self.BASE_URL = BASE_URL
        self.token  = token
    
    def logout(self):
        self.token = None

    def view_challans(self, vehicle_id):
        response = requests.get(f"{self.BASE_URL}toll/get-unsettled-overdue-challan/{vehicle_id}", headers = {"Authorization": self.token})
        return {
            "body": response.json(),
            "status_code": response.status_code
        }

    def view_fastag_balance(self, tag_id):
        response = requests.get(f"{self.BASE_URL}toll/get-balance/{tag_id}", headers = {"Authorization": self.token})
        return {
            "body" : response.json(),
            "status_code": response.status_code
        }

    def vehicle_entry_at_toll(self, vehicle_id, passage_amount):
        toll_data = {
            "passage-amount": passage_amount
        }
        response = requests.post(f"{self.BASE_URL}toll/scan-vehicle/{vehicle_id}", json = toll_data, headers = {"Authorization": self.token})
        return {
            "body" : response.json(),
            "status_code": response.status_code
        }