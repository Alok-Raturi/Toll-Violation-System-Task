from models.vehicle_model import Vehicle
import azure.functions as func
from repositories.vehicle_repo import VehicleRepo
from repositories.user_repo import UserRepo
from repositories.fastag_repo import FastagRepo
from utils.send_email import send_email
import json
import logging

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
        