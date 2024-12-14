import azure.functions as func
import uuid
import json
from azure.cosmos import  exceptions
from email_validator import validate_email,EmailNotValidError
from utils.db_connection import client

rto_triggers = func.Blueprint()

DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"
VEHICLE_CONTAINER = "Vehicle-Table"
FASTAG_CONTAINER = "Fastag-Table"

@rto_triggers.route(route="rto/create-police-man",methods=["POST"])
def create_police_man(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = json.loads(req.get_body().decode('utf-8'))
        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)
        user_id = str(uuid.uuid4())
        name = body['name']
        designation = body['designation']
        password = body['password']
        email = body['email']

        validate_email(email)
        
        if designation == 'police':
            user_container.create_item({
                "id": user_id,
                "name": name,
                "designation": designation,
                "password": password,
                "email":email
            })
            return func.HttpResponse(
                f"Successfully created police man user",
                status_code=201
            )
    except EmailNotValidError:
        return func.HttpResponse(
            "Invalid Email",
            status_code=404
        )
    except KeyError:
        return func.HttpResponse(
            "Invalid body",
            status_code=404
        )
    except exceptions:
        return func.HttpResponse(
            "Internal Server Error",
            status_code=501
        )

@rto_triggers.route(route="rto/create-toll-plaza-man",methods=["POST"])
def create_toll_plaza_man(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = json.loads(req.get_body().decode('utf-8'))
        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)
        user_id = str(uuid.uuid4())
        name = body['name']
        designation = body['designation']
        password = body['password']
        email = body['email']

        validate_email(email)
        
        if designation == 'toll':
            user_container.create_item({
                "id": user_id,
                "name": name,
                "designation": designation,
                "password": password,
                "email":email
            })
            return func.HttpResponse(
                f"Successfully created toll plaza user",
                status_code=201
            )
    except EmailNotValidError:  
        return func.HttpResponse(
            "Invalid Email",
            status_code=404
        )
    except KeyError:
        return func.HttpResponse(
            "Invalid body",
            status_code=404
        )
    except exceptions:
        return func.HttpResponse(
            "Internal Server Error",
            status_code=501
        )

@rto_triggers.route(route="rto/create-vehicle",methods=["POST"])
def create_vehicle(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = json.loads(req.get_body().decode('utf-8'))

        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

        
        user_id = str(uuid.uuid4())
        vehicle_id = body['vehicleId']
        email = body['email']
        name = body['name']
        designation = body['designation']
        password = body['password']


        validate_email(email)

        user_entry= {
            "id": user_id,
            "name": name,
            "designation": designation,
            "password": password,
            "email":email
        }
        vehicle_entry={
            "id": vehicle_id,
            "email": email,
            "tagId":""
        }
        if designation == 'user':  
            query = f"SELECT * FROM c WHERE c.email = '{email}'"
            get_user_by_email = list(user_container.query_items(query=query,enable_cross_partition_query=True))
            if len(get_user_by_email) == 0:
                user_container.create_item(user_entry)
            vehicle_container.create_item(vehicle_entry)
            return func.HttpResponse(
                f"Successfully created vehicle",
                status_code=201
            )
        else:
            return func.HttpResponse(
                "Invalid Designation",
                status_code=404
            )

    except EmailNotValidError:  
        return func.HttpResponse(
            "Invalid Email",
            status_code=404
        )
    except KeyError:
        return func.HttpResponse(
            "Invalid body",
            status_code=404
        )
    except exceptions.CosmosHttpResponseError:
        return func.HttpResponse(
            "Check vehicle Id or there is internal server error",
            status_code=501
        )    

@rto_triggers.route(route="rto/create-fastag",methods=["POST"])
def create_fastag(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = json.loads(req.get_body().decode('utf-8'))

        database = client.get_database_client(DATABASE_NAME)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

        tagid = body['tagId']
        balance = 0
        status = "valid"
        vehicleId = body['vehicleId']
        query = f"SELECT * FROM c WHERE c.id = '{vehicleId}'"
        get_vehicle_by_id = list(vehicle_container.query_items(query=query,enable_cross_partition_query=True))

        if len(get_vehicle_by_id) == 0:
            return func.HttpResponse(
                "Your vehicle id is not valid",
                status_code=404
            )
        current_tagid = get_vehicle_by_id[0]['tagId']
        if current_tagid != "":
            return func.HttpResponse(
                "Your vehicle already has a fastag",
                status_code=404
            )
        vehicle_container.upsert_item(body= {
            "id": vehicleId,
            "email": get_vehicle_by_id[0]['email'],
            "tagId":tagid
        })
        fastag_container.create_item({
            "id": tagid,
            "balance": balance,
            "status": status,
            "vehicleId": vehicleId,
            "email": get_vehicle_by_id[0]['email']
        })
        return func.HttpResponse(
            "Successfully created fastag",
            status_code=201
        )
    except KeyError:
        return func.HttpResponse(
            "Invalid body",
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,exceptions.CosmosResourceExistsError) as e:
        return func.HttpResponse(
            "Internal Server Error",
            status_code=501
        )

