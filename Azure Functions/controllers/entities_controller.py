import azure.functions as func
from azure.cosmos import  exceptions
import json
import logging
from services.transaction_service import TransactionService
from services.challan_service import ChallanService
from services.user_service import UserService
from services.fastag_service import FastagService
from services.vehicle_service import VehicleService


from utils.middleware import user_middleware
from pydantic import ValidationError
from database.models import LoginModel,Challan

entities_triggers = func.Blueprint()

def get_challans(req: func.HttpRequest,user:str) -> func.HttpResponse:
    try:
        vehicle_id = req.route_params.get('vehicleId').strip().upper()
        logging.warning(vehicle_id)
        token = req.headers.get('Authorization')

        if user_middleware(token, user):
            challan_service = ChallanService()
            return challan_service.get_all_challans(vehicle_id)
        else:    
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
    
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception,ValidationError) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 

@entities_triggers.route(route="login",methods=["POST"])
def login(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = json.loads(req.get_body().decode('utf-8'))
        email = body['email'].strip()
        password = body['password']
        login_info = LoginModel(email=email, password=password)
        user_service = UserService()
        return user_service.login(login_info)
    except KeyError:
        logging.error("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        )
    except (ValueError,ValidationError) as e:
        logging.warning("Invalid User Schema according to pydantic module")
        return func.HttpResponse(
            json.dumps("Invalid email or password"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 

@entities_triggers.route(route="user/get-vehicles", methods=["GET"])
def get_vehicles(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = req.headers.get('Authorization')
        data = user_middleware(token,"user")
        if not data:
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        

        email = data['email']
        logging.warning(email)
        
        vehicle_service = VehicleService()
        return vehicle_service.get_vehicles(email)
    
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception,ValidationError) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 
    
@entities_triggers.route(route="user/get-fastags", methods=["GET"])
def get_fastags(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = req.headers.get('Authorization')

        data = user_middleware(token, "user")

        if not data:
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )

        email = data['email']
        logging.warning(email)
        
        fastag_service = FastagService()
        return fastag_service.get_fastags(email)
    
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception,ValidationError) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 

@entities_triggers.route(route="user/recharge-fastag/{tagId}", methods=["POST"])
def recharge_fastag(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = req.headers.get('Authorization')
        if not user_middleware(token, "user"):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        body = json.loads(req.get_body().decode('utf-8'))
        amount = f"{body['amount']}"
        logging.warning(f"Type of amount: {type(amount)}")
        tag_id = req.route_params.get('tagId').strip()

        if not amount.isnumeric():
            logging.error("Invalid amount")
            return func.HttpResponse(
                json.dumps("Invalid amount"),
                status_code = 404
            )
        amount = int(amount)

        fastag_service = FastagService()
        return fastag_service.recharge(tag_id, amount)
        
    
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        )
    except (ValueError,ValidationError,Exception,ValidationError) as e:
        logging.error("Error with validation in transaction schema")
        return func.HttpResponse(
            json.dumps("Wrong schema for Error"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 

@entities_triggers.route(route="user/get-transaction-history/{tagId}", methods=["GET"])
def get_transaction_history(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = req.headers.get('Authorization')
        if not user_middleware(token, "user"):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        tag_id = req.route_params.get('tagId').strip()
        transaction_service = TransactionService()
        return transaction_service.get_history(tag_id)
    
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception,ValidationError) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 

@entities_triggers.route(route="user/get-challans/{vehicleId}", methods=["GET"])
def get_challans_user(req: func.HttpRequest) -> func.HttpResponse:
    return get_challans(req,"user")

@entities_triggers.route(route="police/create-challan",methods=["POST"])
def create_challan(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = req.headers.get('Authorization')

        if not user_middleware(token, "police"):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )

        body = json.loads(req.get_body().decode('utf-8'))
        vehicle_id = body['vehicleId'].strip().upper()
        amount = str(body['amount'])
        location = body['location'].strip()
        description = body['description'].strip()

        if not amount.isnumeric():
            return func.HttpResponse(
                json.dumps("Invalid challan amount"),
                status_code = 404
            )
        amount = int(amount)

        new_challan = Challan(vehicle_id=vehicle_id, amount=amount, location=location, description=description)
        challan_service = ChallanService()
        return challan_service.create_challan(new_challan)

    except KeyError: 
        logging.error("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception,ValidationError) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 
        
@entities_triggers.route(route="police/get-challans/{vehicleId}",methods=["GET"])
def get_challans_police(req: func.HttpRequest) -> func.HttpResponse:
    return get_challans(req,"police")
        
@entities_triggers.route(route="toll/get-unsettled-overdue-challan/{vehicleId}",methods=["GET"])
def get_unsettled_overdue_challans(req: func.HttpRequest) -> func.HttpResponse:
    try:
        vehicle_id = req.route_params.get('vehicleId')
        token = req.headers.get('Authorization')

        if not user_middleware(token, "toll"):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        
        challan_service = ChallanService()
        return challan_service.get_unsettled_overdue_challans(vehicle_id)
    
    except (exceptions.CosmosHttpResponseError,Exception,ValidationError) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 
    
@entities_triggers.route(route="toll/get-balance/{tagId}", methods=["GET"])
def get_balance(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.warning("Route get-balance called")
        tag_id = req.route_params.get('tagId').strip().upper()
        logging.warning(tag_id)
        token = req.headers.get('Authorization')

        if not user_middleware(token, "toll"):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        
        fastag_service = FastagService()
        return fastag_service.get_balance(tag_id)
    
    except (exceptions.CosmosHttpResponseError,Exception,ValidationError) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 


    







@entities_triggers.route(route="user/pay-all-challan/{vehicleId}", methods=["POST"])
def pay_all_challans(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = req.headers.get('Authorization')
        data = user_middleware(token,"user")
        if not data:
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        vehicle_id = req.route_params.get('vehicleId').strip()
        email = data['email']
        challan_service = ChallanService()
        return challan_service.pay_all_challans(vehicle_id,email)
    
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception,ValidationError) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 


@entities_triggers.route(route="user/pay-a-challan/{challanId}", methods=["POST"])
def pay_a_challan(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = req.headers.get('Authorization')
        data = user_middleware(token,"user")

        if not data:
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        email = data['email']
        logging.warning(email)
        challan_id = req.route_params.get('challanId').strip()
        logging.warning(challan_id)
        challan_service = ChallanService()
        return challan_service.pay_a_challan(challan_id,email)
    
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,Exception,ValidationError) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        ) 


@entities_triggers.route(route="toll/scan-vehicle", methods=["POST"])
def scan_vehicle(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = req.headers.get('Authorization')
        if not user_middleware(token, "toll"):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        logging.warning("Token validated")
        
        body = json.loads(req.get_body().decode('utf-8'))
        passage_amount = body['passageAmount']
        vehicle_id = body['vehicleId']
        toll_location = body['location']

        if not passage_amount.isnumeric():
            return func.HttpResponse(
                json.dumps("Passage amount is not valid."),
                status_code=404
            )
        vehicle_service = VehicleService()
        return vehicle_service.scan_vehicle(vehicle_id, int(passage_amount), toll_location)

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
    

