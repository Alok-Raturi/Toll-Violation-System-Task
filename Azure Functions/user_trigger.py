import json
import azure.functions as func
from azure.cosmos import  exceptions
from utils.db_connection import client, encode_token
from jose import JWTError
import logging

DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"
VEHICLE_CONTAINER = "Vehicle-Table"
CHALLAN_CONTAINER = "Challan-Table"
FASTAG_CONTAINER = "Fastag-Table"
TRANSACTION_CONTAINER = "Transaction-Table"

user_trigger = func.Blueprint()

# login - done
# get vehicles associated with that email - done 
# get all fastag - done
# get challans associated with email - done
# pay all the challans
# recharge fastag
# view transaction history


@user_trigger.route(route="user/login", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def login_user(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = json.loads(req.get_body().decode('utf-8'))

        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)

        email = body['email']
        password = body['password']

        query = "SELECT * FROM c WHERE c.email = @email and c.password = @password"
        items = list(user_container.query_items(
            query=query,
            parameters=[
                {"name": "@email", "value": email},
                {"name": "@password", "value": password}
            ],
            enable_cross_partition_query=True
        ))

        if len(items) == 0:
            return func.HttpResponse(
                "Invalid Email or Password",
                status_code=404
            )
        else:
            if(items[0]['designation'] != "user"):
                return func.HttpResponse(
                    "You are not a user.",
                    status_code=404
                )
            token = encode_token({
                "email":email,
                "designation":items[0]['designation'],
                "id":items[0]['id']
            })
            return func.HttpResponse(
                token,
                status_code=200
            )
    except KeyError:
        return func.HttpResponse(
            "Invalid body",
            status_code=404
        )
    except (JWTError, Exception) as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )
    
@user_trigger.route(route="user/get-challan/{email}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def get_challan(req: func.HttpRequest) -> func.HttpResponse:
    try:
        database = client.get_database_client(DATABASE_NAME)
        vechicle_container = database.get_container_client(VEHICLE_CONTAINER)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)

        email = req.route_params.get('email')
         
        query = 'Select c.id from c where c.email = "{0}"'.format(email)

        item = list(vechicle_container.query_items(query=query,enable_cross_partition_query=True))
        vehicleIds= tuple(i['id'] for i in item)

        get_challan_query = 'Select * from c where c.vehicleId IN {0}'.format(vehicleIds)
        challans = list(challan_container.query_items(get_challan_query,enable_cross_partition_query=True))

        return func.HttpResponse(
            body=json.dumps(challans),
            status_code=200
        )
    except (exceptions.CosmosHttpResponseError,Exception) as e:
        return func.HttpResponse(
            "Error",
            status_code=404
        )
    
@user_trigger.route(route="user/get-vehicle/{email}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def get_vehicle(req: func.HttpRequest) -> func.HttpResponse:
    try:
        database = client.get_database_client(DATABASE_NAME)
        vechicle_container = database.get_container_client(VEHICLE_CONTAINER)

        email = req.route_params.get('email')

        query = 'Select * from c where c.email = "{0}"'.format(email)

        vehicles = list(vechicle_container.query_items(query=query,enable_cross_partition_query=True))

        return func.HttpResponse(
            body=json.dumps(vehicles),
            status_code=200
        )
    except (exceptions.CosmosHttpResponseError,Exception) as e:
        return func.HttpResponse(
            "Error",
            status_code=404
        )

@user_trigger.route(route="user/get-fastags/{email}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def get_fastags(req: func.HttpRequest) -> func.HttpResponse:
    try:
        database = client.get_database_client(DATABASE_NAME)
        vechicle_container = database.get_container_client(VEHICLE_CONTAINER)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)

        email = req.route_params.get('email')

        query = 'Select c.id from c where c.email = "{0}"'.format(email)

        item = list(vechicle_container.query_items(query=query,enable_cross_partition_query=True))
        vehicleIds= tuple(i['id'] for i in item)

        get_challan_query = 'Select * from c where c.vehicleId IN {0}'.format(vehicleIds)
        fastag_information = list(fastag_container.query_items(get_challan_query,enable_cross_partition_query=True))

        return func.HttpResponse(
            body=json.dumps(fastag_information),
            status_code=200
        )

    except (exceptions.CosmosHttpResponseError,Exception) as e:
        return func.HttpResponse(
            "Error",
            status_code=404
        )
    
