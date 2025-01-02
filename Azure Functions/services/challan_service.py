from repositories.challan_repo import ChallanRepo
from repositories.vehicle_repo import VehicleRepo
from models.challan_model import Challan
from utils.send_email import send_email
import azure.functions as func
import json
import logging

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

class ChallanSerice:
    def __init__(self):
        self.challan_repo = ChallanRepo()

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
    
    def pay_a_challan(self, challan_id):
        challan_details = self.challan_repo.does_challan_exist(challan_id)
        if not challan_details:
            logging.error("This challan does not exist")
            return func.HttpResponse(
                json.dumps("This challan does not exist"),
                status_code = 404
            )
        self.challan_repo.pay_a_challan(challan_id, challan_details[0]['vehicleId'])
        logging.warning("Challan paid successfully")
        return func.HttpResponse(
            json.dumps("Challan paid successfully"),
            status_code = 200
        )
    
    def pay_all_challans(self, vehicle_id):
        challans = self.challan_repo.get_all_challans(vehicle_id)
        if not challans:
            logging.error("No Challans for this vehicle")
            return func.HttpResponse(
                json.dumps("No Challans for this vehicle"),
                status_code = 404
            )
        is_paid = self.challan_repo.pay_all_challans(challans, vehicle_id)
        if is_paid:
            logging.warning("No unsettled challlans for this vehicle")
            return func.HttpResponse(
                json.dumps("Paid all unsettled challans"),
                status_code = 200
            )
        else:
            logging.error("No unsettled challlans for this vehicle")
            return func.HttpResponse(
                json.dumps("No unsettled challlans for this vehicle"),
                status_code = 404
            )