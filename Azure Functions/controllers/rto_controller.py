import azure.functions as func
from azure.cosmos import  exceptions
import json
import logging
from helper.vehicle_number import generate_vehicle_number
from helper.fastag_number import generate_dummy_fastag_id

from services.user_service import UserService
from services.vehicle_service import VehicleService
from services.fastag_service import FastagService
from pydantic import ValidationError
from database.models import User,Vehicle,Fastag

rto_triggers = func.Blueprint()

def extract_details(req):
    body = json.loads(req.get_body().decode('utf-8'))
    return (body['name'].strip(), body['password'].strip(), body['email'].strip())

@rto_triggers.route(route="rto/create-police-man",methods=["POST"])
def create_police_man(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.warning("Creating Police Man")
        
        (name, password, email) = extract_details(req)
        police_person = User(name=name, designation="police", email=email, password=password)
        user_service = UserService()

        return user_service.create_user(police_person)
    except (ValueError,ValidationError) as e:
        logging.warning("Invalid User Schema according to pydantic module")
        return func.HttpResponse(
            json.dumps("Invalid fields"),
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

        toll_person = User(name=name, designation="toll", email=email, password=password)
        user_service = UserService()
        return user_service.create_user(toll_person)

    except (ValueError,ValidationError) as e:
        logging.warning("Invalid User Schema according to pydantic module")
        return func.HttpResponse(
            json.dumps("Invalid fields"),
            status_code=404
        )
    except KeyError:
        logging.warning("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        ) 
    except (exceptions.CosmosHttpResponseError,Exception) as e:
        logging.warning("Abc")
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

        vehicle_owner = User(name=name, designation="user",email=email, password=password)
        user_service = UserService()
        return user_service.create_user(vehicle_owner)

    except (ValueError,ValidationError) as e:
        logging.warning("Invalid User Schema according to pydantic module")
        return func.HttpResponse(
            json.dumps("Invalid fields"),
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
        vehicle_id = generate_vehicle_number()
        email = body['email'].strip()
        
        new_vehicle = Vehicle(id=vehicle_id, email=email,tag_id="")
        vehicle_service = VehicleService()
        return vehicle_service.create_vehicle(new_vehicle)

    except KeyError:
        logging.error("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        )
    except (ValueError,ValidationError) as e:
        logging.warning(e)
        logging.warning("Invalid User Schema according to pydantic module")
        return func.HttpResponse(
            json.dumps("Invalid fields"),
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
        tag_id = generate_dummy_fastag_id()
        vehicle_id = body['vehicleId'].strip()

        new_fastag = Fastag(id=tag_id, balance=0, vehicle_id=vehicle_id,status="valid",email="test@gmail.com")
        fastag_service = FastagService()
        return fastag_service.create_fastag(new_fastag)

    except KeyError:
        logging.error("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        )
    except (ValueError,ValidationError) as e:
        logging.warning(e)
        logging.warning("Invalid User Schema according to pydantic module")
        return func.HttpResponse(
            json.dumps("Invalid fields"),
            status_code=404
        )

    except (exceptions.CosmosHttpResponseError,Exception) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        )    