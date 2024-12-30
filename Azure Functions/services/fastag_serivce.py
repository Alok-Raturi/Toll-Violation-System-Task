from repositories.fastag_repo import FastagRepo
from repositories.vehicle_repo import VehicleRepo
from models.fastag_model import Fastag
from utils.send_email import send_email
import logging
import json
import azure.functions as func

FASTAG_ISSUED_SUBJECT = "Thank you for purchasing a fastag"
FASTAG_ISSUED_BODY = """
Thank you for purchasing a fastag.<br>
Your fastag is successfully registered with us.<br>
Your fastag id is {0}.<br>
Your vehicle id is {1}.<br>
Right now your fastag has a balance of Rs.{2}.<br>
You can use this fastag for any future toll payments.<br>
Please use this id for any future reference.
"""

class FastagService:
    def __init__(self):
        self.fastag_repo = FastagRepo()

    def create_fastag(self, fastag: Fastag):
        # Checking whether fastag already exists or not
        if self.fastag_repo.does_fastag_exists(fastag.id):
            logging.error("Fastag already exists")
            return func.HttpResponse(
                json.dumps("Fastag already exists"),
                status_code = 404
            )
        
        
        # Checking whether vehicle exists 
        vehicle_repo = VehicleRepo()
        vehicle_details = vehicle_repo.does_vehicle_exists(fastag.vehicle_id)
        if not vehicle_details:
            logging.error("No vehicle with this id")
            return func.HttpResponse(
                json.dumps("No vehicle with this id"),
                status_code = 404
            )
        
        fastag.email = vehicle_details[0]['email']
        previous_tag_id = vehicle_details[0]['tagId']
        
        logging.warning(f"Owner Email: {fastag.email}")
        logging.warning(f"Previous Tag Id: {previous_tag_id}")

        if previous_tag_id != "":
            # Fastag already attached to this vehicle
            logging.error("Fastag already attached to this vehicle")
            return func.HttpResponse(
                json.dumps("Fastag already attached to this vehicle"),
                status_code = 404
            )

        self.fastag_repo.create_fastag(fastag)
        logging.warning("Fastag Created")

        vehicle_repo.issue_fastag(fastag.id, fastag.vehicle_id, fastag.email)
        logging.warning("Fastag issued")

        send_email(
            fastag.email,
            FASTAG_ISSUED_SUBJECT,
            FASTAG_ISSUED_BODY.format(
                fastag.id,
                fastag.vehicle_id,
                fastag.balance
            )
        )
        logging.warning("Email sent to user")

        return func.HttpResponse(
            json.dumps("Successfully created and issued fastag"),
            status_code=201
        )


