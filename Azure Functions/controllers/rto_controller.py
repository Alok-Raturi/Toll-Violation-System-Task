import azure.functions as func
from azure.cosmos import  exceptions
import json
import logging
from email_validator import EmailNotValidError
from models.user_model import User
from models.vehicle_model import Vehicle
from models.fastag_model import Fastag
from services.user_service import UserService
from services.vehicle_service import VehicleService
from services.fastag_serivce import FastagService


rto_triggers = func.Blueprint()

def extract_details(req: func.HttpRequest):
    body = json.loads(req.get_body().decode('utf-8'))
    return (body['name'], body['password'], body['email'])

@rto_triggers.route(route="rto/create-police-man",methods=["POST"])
def create_police_man(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.warning("Creating Police Man")
        
        (name, password, email) = extract_details(req)
        police_person = User(name, "police", email, password)
        user_service = UserService()

        # Calling service function here to create policeman, validate email, check password strength
        return user_service.create_user(police_person)

    except EmailNotValidError:
        logging.error("Invalid email")
        return func.HttpResponse(
            json.dumps("Invalid Email"),
            status_code=404
        )
    except KeyError:
        logging.warning("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        ) 
    except (exceptions.CosmosHttpResponseError,Exception) as e:
        logging.warning(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        )

@rto_triggers.route(route="rto/create-toll-person",methods=["POST"])
def create_toll_plaza_man(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.warning("Creating Toll Person")
        (name, password, email) = extract_details(req)

        toll_person = User(name, "toll", email, password)
        # Calling service function here to create toll person
        user_service = UserService()
        return user_service.create_user(toll_person)

    except EmailNotValidError:
        logging.error("Invalid email")
        return func.HttpResponse(
            json.dumps("Invalid Email"),
            status_code=404
        )
    except KeyError:
        logging.warning("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        ) 
    except (exceptions.CosmosHttpResponseError,Exception) as e:
        logging.warning(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        )

@rto_triggers.route(route="rto/create-vehicle-owner",methods=["POST"])
def create_vehicle_owner(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.warning("Creating Toll Person")
        (name, password, email) = extract_details(req)

        vehicle_owner = User(name, "user", email, password)
        # Calling service function here to create vehicle owner
        user_service = UserService()
        return user_service.create_user(vehicle_owner)

    except EmailNotValidError:
        logging.error("Invalid email")
        return func.HttpResponse(
            json.dumps("Invalid Email"),
            status_code=404
        )
    except KeyError:
        logging.warning("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        ) 
    except (exceptions.CosmosHttpResponseError,Exception) as e:
        logging.warning(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        )

@rto_triggers.route(route="rto/create-vehicle",methods=["POST"])
def create_vehicle(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info("Creating vehicle and owner")
        body = json.loads(req.get_body().decode('utf-8'))
        vehicle_id = body['vehicleId']
        email = body['email']
        
        # Calling service function here to create toll person
        new_vehicle = Vehicle(vehicle_id, email)
        vehicle_service = VehicleService()
        return vehicle_service.create_vehicle(new_vehicle)

    except KeyError:
        logging.error("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception) as ex:
        logging.error(ex)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        )    
    
@rto_triggers.route(route="rto/create-fastag",methods=["POST"])
def create_fastag(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info("Issuing fastag to vehicle")
        body = json.loads(req.get_body().decode('utf-8'))
        tag_id = body['tagId']
        vehicle_id = body['vehicleId']

        new_fastag = Fastag(tag_id, 0, vehicle_id)
        # Creating Fastag and attaching to the vehicle
        fastag_service = FastagService()
        return fastag_service.create_fastag(new_fastag)

    except KeyError:
        logging.error("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        )    