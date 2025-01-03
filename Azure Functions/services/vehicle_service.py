
import azure.functions as func
from services.transaction_service import TransactionRepo
from repositories.vehicle_repo import VehicleRepo
from repositories.challan_repo import ChallanRepo
from repositories.fastag_repo import FastagRepo
from repositories.user_repo import UserRepo

from database.models import Vehicle,Transaction

from helper.send_email import send_email
import json
import logging
import datetime
import pytz

VEHICLE_ISSUED_SUBJECT = "Thank you for purchasing a vehicle"
VEHICLE_ISSUED_BODY = """
Thank you for purchasing a vehicle and registering it with us.<br>
Your vehicle is successfully registered with us.<br>
Your vehicle id is {0}.<br>
Your email id is {1}.<br>
Right now your vehicle does not have a fastag.<br>
You can purchase a fastag.<br>
Please use this id for any future reference.
"""


class VehicleService:
    def __init__(self):
        self.vehicle_repo = VehicleRepo()

    def create_vehicle(self, vehicle: Vehicle):
        user_repo = UserRepo()
        if not user_repo.does_vehicle_owner_exists(vehicle.email):
            # User does not exist
            logging.error("No vehicle owner with this email")
            return func.HttpResponse(
                json.dumps("No vehicle owner with this email"),
                status_code = 404
            )
        
        if self.vehicle_repo.does_vehicle_exists(vehicle.id):
            # Vehicle already exists
            logging.warning("Vehicle already exists with this id")
            return func.HttpResponse(
                json.dumps("Vehicle already exists with this id"),
                status_code = 404
            )

        self.vehicle_repo.create_vehicle(vehicle)
        logging.warning("Vehicle created successfully")
        send_email(
            vehicle.email,
            VEHICLE_ISSUED_SUBJECT,
            VEHICLE_ISSUED_BODY.format(
                vehicle.id,
                vehicle.email
            )
        )
        logging.warning("Email sent to vehicle owner")
        return func.HttpResponse(
            json.dumps("Successfully created vehicle"),
            status_code=201
        )

    def scan_vehicle(self, vehicle_id, passage_amount, toll_location):
        vehicle_details = self.vehicle_repo.does_vehicle_exists(vehicle_id)
        if not vehicle_details:
            logging.error("No Vehicle with this id")
            return func.HttpResponse(
                json.dumps("No Vehicle with this id"),
                status_code = 404
            )
        logging.warning("Vehicle Exists")

        tag_id = vehicle_details[0]['tagId']
        owner_email = vehicle_details[0]['email']

        if tag_id == '':
            logging.error("No Fastag issued for the vehicle. Issue a Fastag first" )
            return func.HttpResponse(
                json.dumps("No Fastag issued for the vehicle. Issue a Fastag first"),
                status_code=404
            )
        logging.warning(f"Tag id: {tag_id}")

        # Validating fastag
        fastag_repo = FastagRepo()
        fastag_details = fastag_repo.does_fastag_exists(tag_id)

        if not fastag_details:
            logging.error("No fastag with this id")
            return func.HttpResponse(
                json.dumps("Internal server error"),
                status_code = 500
            )
        
        status = fastag_details[0]['status']
        remaining_balance = float(fastag_details[0]['balance'])

        # Validating fastag status
        if status == "invalid":
            logging.error("Can't Proceed as your Fastag is blacklisted!!!")
            return func.HttpResponse(
                json.dumps("Can't Proceed as your Fastag is blacklisted!!! \nTip: Contact RTO Office for resolution"),
                status_code = 404
            )

        challan_repo = ChallanRepo()
        challans = challan_repo.get_unsettled_overdue_challans(vehicle_id)
        
        transaction_repo = TransactionRepo()
        fastag_repo = FastagRepo()
        # No challan: Deduct passage amount and pass
        if len(challans) == 0:
            if remaining_balance >= passage_amount:
                logging.warning('Case 1 - a')
                
                timestamp = str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"))

                new_transaction = Transaction(tag_id=tag_id,type='debit', amount=challan['amount'], timestamp=timestamp,description="toll plaza payment",location=toll_location)
                self.transaction_repo.create_transaction(new_transaction)

                
                # Update fastag balance
                fastag_repo.set_balance(
                    tag_id, 
                    remaining_balance - passage_amount,
                    vehicle_id,
                )

                return func.HttpResponse(
                    json.dumps("Passage Granted"),
                    status_code = 200
                )
            else:
                logging.warning('Case 1 - b')
                logging.error("Insufficient Balance for passage")
                return func.HttpResponse(
                    json.dumps("Passage Blocked!!!  Insufficient Balance for passage"),
                    status_code = 404                
                )

        total = 0
        for challan in challans:
            total = total + challan['amount']
        
        logging.warning(f"Total overdue challan amount: {total}")

        if remaining_balance >= total + passage_amount:
            # Deduct total amount, change challans status and pass
            logging.warning('Case 2 - a')
            
            # Settle overdue challans
            challan_repo.settle_all_overdue_challans(challans, vehicle_id)

            timestamp = str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"))

            new_transaction = Transaction(tag_id=tag_id,type='debit', amount=total, timestamp=timestamp,description="forced overdue challan payment",location=toll_location)
            self.transaction_repo.create_transaction(new_transaction)

            timestamp = str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"))

            new_transaction = Transaction(tag_id=tag_id,type='debit', amount=passage_amount, timestamp=timestamp,description="toll plaza payment",location=toll_location)
            self.transaction_repo.create_transaction(new_transaction)

            fastag_repo.set_balance(
                tag_id, 
                remaining_balance - passage_amount - total,
                vehicle_id,
            )

            return func.HttpResponse(
                json.dumps("Passage Granted, paid overdue challans"),
                status_code = 200
            )

        elif remaining_balance >= passage_amount:
            # Deduct passage amount, block fastag and pass
            logging.warning('Case 2 - b')
            timestamp = str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"))

            new_transaction = Transaction(tag_id=tag_id,type='debit', amount=passage_amount, timestamp=timestamp,description="toll plaza payment",location=toll_location)
            self.transaction_repo.create_transaction(new_transaction)

            fastag_repo.set_balance(
                tag_id, 
                remaining_balance - passage_amount,
                vehicle_id,
            )
            fastag_repo.change_status(tag_id, "invalid", vehicle_id)
        
            return func.HttpResponse(
                json.dumps("Passage Granted but Fastag blacklisted as insufficient balance for overdue challans"),
                status_code = 200
            )
        else:
            # Block fastag and don't pass
            logging.warning('Case 2 - c')
            fastag_repo.change_status(tag_id, "invalid", vehicle_id)
            logging.error("Fastag blacklisted as insufficient balance for passage and overdue challans")
            return func.HttpResponse(
                json.dumps("Passage Blocked!!! and Fastag blacklisted as insufficient balance for passage and overdue challans"),
                status_code= 404
            )
            
    def get_vehicles(self, email):
        user_repo = UserRepo()
        if not user_repo.does_user_exists(email):
            logging.error("No user with this email")
            return func.HttpResponse(
                json.dumps("No user with this email"),
                status_code = 404
            )
        vehicles = self.vehicle_repo.get_vehicles(email)
        if len(vehicles) == 0:
            logging.error("No vehicles found")
            return func.HttpResponse(
                json.dumps("No Vehicles found"),
                status_code=404
            )
        return func.HttpResponse(
            json.dumps(vehicles),
            status_code = 200
        )
