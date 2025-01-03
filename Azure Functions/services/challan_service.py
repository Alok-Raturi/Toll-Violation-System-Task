from repositories.challan_repo import ChallanRepo
from repositories.vehicle_repo import VehicleRepo
from repositories.fastag_repo import FastagRepo
from repositories.transaction_repo import TransactionRepo
from database.models import Challan,Transaction
from helper.send_email import send_email
import azure.functions as func
import json
import logging
import datetime
import pytz

CHALLAN_SUBJECT ="Challan created for your vehicle with vehicle number - {0}"
CHALLAN_BODY = """
Respected Sir,<br>
You have violated the traffic laws.<br>
A challan is issued to you.<br>
&emsp;<b>Vehicle Number</b>: {0}<br>
&emsp;<b>Amount</b>: RS: {1}<br>
&emsp;<b>Location</b>: {2}<br>
&emsp;<b>Description</b>: {3}<br>
You have to pay this challan within next 90 days from this day onwards to avoid future complications.
"""

class ChallanService:
    def __init__(self):
        self.challan_repo = ChallanRepo()
        self.vehicle_repo = VehicleRepo()
        self.fastag_repo = FastagRepo()
        self.transaction_repo = TransactionRepo()

    def create_challan(self, challan: Challan):
        vehicle_repo = VehicleRepo()
        vehicle_details = vehicle_repo.does_vehicle_exists(challan.vehicle_id)
        if not vehicle_details:
            return func.HttpResponse(
                json.dumps("No vehicle with this id"),
                status_code = 404
            )
        
        self.challan_repo.create_challan(challan)
        logging.warning("Challan created")

        send_email(
            vehicle_details[0]['email'], 
            CHALLAN_SUBJECT.format(challan.vehicle_id),
            CHALLAN_BODY.format(
                challan.vehicle_id, 
                challan.amount, 
                challan.location, 
                challan.description
            )
        )

        return func.HttpResponse(
            json.dumps("Challan created"),
            status_code = 201
        )

    def get_all_challans(self, vehicle_id):
        vehicle_repo = VehicleRepo()
        if not vehicle_repo.does_vehicle_exists(vehicle_id):
            return func.HttpResponse(
                json.dumps("No vehicle with this id"),
                status_code = 404
            )
        
        challans = self.challan_repo.get_all_challans(vehicle_id)
        if len(challans) == 0:
            return func.HttpResponse(
                json.dumps("No challans for this vehicle"),
                status_code = 404
            )
        
        return func.HttpResponse(
            json.dumps(challans),
            status_code = 200
        )
    
    def get_unsettled_overdue_challans(self, vehicle_id):
        vehicle_repo = VehicleRepo()
        if not vehicle_repo.does_vehicle_exists(vehicle_id):
            return func.HttpResponse(
                json.dumps("No vehicle with this id"),
                status_code = 404
            )
        
        challans = self.challan_repo.get_unsettled_overdue_challans(vehicle_id)
        if len(challans) == 0:
            logging.error("No unsettled overdue challans")
            return func.HttpResponse(
                json.dumps("No unsettled overdue challans"),
                status_code = 404
            )
        return func.HttpResponse(
            json.dumps(challans),
            status_code = 200
        )
    
    def pay_a_challan(self, challan_id,email):
        challan_details = self.challan_repo.does_challan_exist(challan_id)
        if not challan_details:
            logging.error("This challan does not exist")
            return func.HttpResponse(
                json.dumps("This challan does not exist"),
                status_code = 404
            )
        
        if challan_details[0]['status']=="settled":
            return func.HttpResponse(
                json.dumps("Challan is already paid."),
                status_code=404
            )
        vehicle_id = challan_details[0]['vehicleId']
        challan_amount = challan_details[0]['amount']

        logging.warning(vehicle_id)
        logging.warning(challan_amount)

        check_vehicle_association = self.vehicle_repo.check_associated_email_with_vehicle(vehicle_id,email)
        if check_vehicle_association==False:
            return func.HttpResponse(
                json.dumps("You are not associated with this vehicle."),
                status_code=404
            )
        
        fastag_info = self.fastag_repo.get_fastag_by_vehicle(vehicle_id)
        if len(fastag_info)==0:
            return func.HttpResponse(
                json.dumps("No fastag associated with the vehicle."),
                status_code=404
            )
        
        if fastag_info[0]['status']!='valid':
            return func.HttpResponse(
                json.dumps("Your fastag is blacklisted. Visit nearby RTO office to settle your dues."),
                status_code=404
            )
        
        fastag_balance = int(fastag_info[0]['balance'])

        if fastag_balance<challan_amount:
            return func.HttpResponse(
                json.dumps("Associated fastag do not have enough balance. Please recharge it."),
                status_code=404
            )

        new_balance = int(fastag_info[0]['balance'])- int(challan_amount)
        self.fastag_repo.set_balance(tag_id=fastag_info[0]['id'],new_balance=new_balance,vehicle_id=vehicle_id)

        logging.warning(check_vehicle_association)
        self.challan_repo.pay_a_challan(challan_id, challan_details[0]['vehicleId'])
        timestamp = str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"))

        new_transaction = Transaction(tag_id=fastag_info[0]['id'],type='debit', amount=challan_amount, timestamp=timestamp,description="challan payment",location="online")
        self.transaction_repo.create_transaction(new_transaction)

        logging.warning("Challan paid successfully")
        return func.HttpResponse(
            json.dumps("Challan paid successfully"),
            status_code = 200
        )
    
    def pay_all_challans(self, vehicle_id,email):
        check_vehicle_association = self.vehicle_repo.check_associated_email_with_vehicle(vehicle_id,email)
        if check_vehicle_association==False:
            return func.HttpResponse(
                json.dumps("You are not associated with this vehicle."),
                status_code=404
            )
        challans = self.challan_repo.get_all_unsettled_challan(vehicle_id)

        if not challans:
            logging.error("No Challans for this vehicle")
            return func.HttpResponse(
                json.dumps("No Challans for this vehicle"),
                status_code = 404
            )
        
        amount = 0
        for item in challans:
            amount+= int(item['amount'])

        fastag_info = self.fastag_repo.get_fastag_by_vehicle(vehicle_id=vehicle_id)

        if len(fastag_info) == 0:
            return func.HttpResponse(
                json.dumps("No Fastag found"),
                status_code=404
            )
        
        if fastag_info[0]['status']!='valid':
            return func.HttpResponse(
                json.dumps("Your fastag is blacklisted. Visit nearby RTO office to settle your dues."),
                status_code=404
            )
        
                   
        logging.warning(fastag_info[0]['balance'])
        logging.warning(amount)


        if int(fastag_info[0]['balance']) < amount:
            logging.warning(fastag_info[0]['balance'])
            logging.warning(amount)
            return func.HttpResponse(
                json.dumps("Insufficient Balance"),
                status_code=404
            )
        
        tag_id = fastag_info[0]['id']
        new_balance = int(fastag_info[0]['balance']) - amount

        self.fastag_repo.set_balance(tag_id=tag_id,new_balance=new_balance,vehicle_id=vehicle_id)

        for challan in challans:
            self.challan_repo.pay_a_challan(challan['id'],vehicle_id)
            timestamp = str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"))

            new_transaction = Transaction(tag_id=fastag_info[0]['id'],type='debit', amount=challan['amount'], timestamp=timestamp,description="challan payment",location="online")
            self.transaction_repo.create_transaction(new_transaction)
            logging.warning("Challan paid successfully")

        return func.HttpResponse(
            json.dumps("Challan paid successfully"),
            status_code = 200
        )
    
