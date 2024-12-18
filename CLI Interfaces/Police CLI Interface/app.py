import requests
import json

PROMPT ="""
PRESS 1 FOR LOGIN
PRESS 2 FOR EXIT
"""

BASE_URL = "http://localhost:7071/api/"

PROMPT_AFTER_LOGIN = """
PRESS 1 FOR CREATING A CHALLAN
PRESS 2 FOR VIEWING CHALLAN OF A VEHICLE 
PRESS 3 FOR LOGOUT
"""

class Traffic_Police:
    def __init__(self,email,password):
        self.email = email
        self.password = password
    
    def login(self):
        auth_data =  json.dumps({"email":self.email,"password":self.password})
        response = requests.post(BASE_URL + "police/login",data=auth_data)
        if(response.status_code==200):
            self.token = response.json()['access_token']
        return {
            "status":response.status_code,
            "body": response.json()
        }
    
    def view_vehicle_challan(self,vehicle_number):
        response = requests.get(f"{BASE_URL}police/get-challan/{vehicle_number}",headers={"Authorization":self.token})
        return {
            "status":response.status_code,
            "data":response.json(),
        }
    
    def create_challan(self,vehicleId,amount,description,location):
        challan_data =json.dumps({
            "vehicleId":vehicleId,
            "amount":amount,
            "description":description,
            "location":location
        })
        response = requests.post(BASE_URL + "police/create-challan",data=challan_data,headers={"Authorization":self.token})
        return {
            "status":response.status_code,
            "data":response.json(),
        }

    def logout(self):
        self.email=None
        self.password= None
        self.token=None
        
if __name__ == '__main__':
    print(PROMPT)
    choice = input("Enter your choice: ")
    if choice == '1':
        print("---------------- LOGIN ----------------")
        username = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        traffic_police = Traffic_Police(username,password)
        login = traffic_police.login()

        if login['status']==200:
            print("-----------------  Login Successful ------------- ")
            while(True):
                print(PROMPT_AFTER_LOGIN)
                choice = input("Enter your choice: ")
                if choice == '1':
                    print("------------- Enter Details to create challan ---------------")
                    vehicleId = input("Enter vehicle number: ")
                    amount = input("Enter amount: ")
                    description = input("Enter description: ")
                    location = input("Enter location: ")
                    response = traffic_police.create_challan(vehicleId,amount,description,location)
                    if response['status']==200 or response['status']==201:
                        print(response['data'])
                    else:
                        print(response['data'])

                elif choice == '2':
                    vehicleId = input("Enter vehicle number: ")
                    response = traffic_police.view_vehicle_challan(vehicleId)
                    if response['status']==200:
                        challan_list = list(response['data'])
                        print("---------------------- All Challans ------------------")
                        for challan in challan_list:
                            print(f"{challan['id']}\t{challan['amount']}\t{challan['location']}\t{challan['status']}\t{challan['description']}")
                    else:
                        print(response['data'])

                elif choice == '3':
                    print("Logging you out.....")
                    traffic_police.logout()
                    del traffic_police
                    print("------------ Successfully logged you out ----------------")
                    break
                else:
                    print("Invalid choice. Try again...")
        else:
            print(login['body'])

    elif choice == '2':
        print("Exit")
    else:
        print("Invalid choice. Exiting...")