import azure.functions as func
import json
from utils.db_connection import client
from utils.jwt_decode import encode_token, decode_token
from utils.password import check_password
from jose import JWTError
from azure.cosmos import  exceptions
import datetime
import time
import logging
from utils.send_email import send_email

police_trigger = func.Blueprint()

DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"
VEHICLE_CONTAINER = "Vehicle-Table"
CHALLAN_CONTAINER = "Challan-Table"
FASTAG_CONTAINER = "Fastag-Table"
TRANSACTION_CONTAINER = "Transaction-Table"

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


def police_middleware(token:str):
    try:
        data = decode_token(token)
        if data['designation'] != "police":
            return False
        return True
    except JWTError:
        return False


@police_trigger.route(route="police/login", auth_level=func.AuthLevel.ANONYMOUS,methods=["POST"])
def police_login(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = json.loads(req.get_body().decode('utf-8'))
        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)
        email = body['email']
        password = body['password']

        query = "SELECT * FROM c WHERE c.email = '{0}' and c.designation='police'".format(email)

        items = list(user_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        if len(items) == 0:
            logging.error("Invalid Email or Password")
            return func.HttpResponse(
                json.dumps("Invalid Email or Password"),
                status_code=404
            )

        if not check_password(password, items[0]['password']):
            logging.error("Incorrect password")
            return func.HttpResponse(
                json.dumps("Invalid Email or Password"),
                status_code=404
            )

        token = encode_token({
            "email":email,
            "designation":items[0]['designation'],
            "id":items[0]['id']
        })
        logging.info("Login Success")
        return func.HttpResponse(
            body=json.dumps({
                "access_token":token
            }),
            status_code=200
        )
    except KeyError:
        logging.error("Invalid Body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        )
    except (JWTError, Exception,exceptions.CosmosHttpResponseError) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=500
        )


@police_trigger.route(route="police/get-challan/{vehicleId}", auth_level=func.AuthLevel.ANONYMOUS,methods=["GET"])
def get_challan_by_vehicle_id(req: func.HttpRequest) -> func.HttpResponse:
    try:
        vehicleId = req.route_params.get('vehicleId')
        token = req.headers.get('Authorization')
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        logging.warn(token)
        if not police_middleware(token):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )

        database = client.get_database_client(DATABASE_NAME)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

        query = "SELECT * FROM c WHERE c.id = @vehicleId"
        items = list(vehicle_container.query_items(
            query= query,
            parameters=[
                {"name":"@vehicleId","value":vehicleId}
            ],
            enable_cross_partition_query=True
        ))

        if(len(items)==0):
            return func.HttpResponse(
                json.dumps("Invalid vehicle Id"),
                status_code=500
            )

        query = "SELECT * FROM c WHERE c.vehicleId = @vehicleId"
        items = list(challan_container.query_items(
            query=query,
            parameters=[
                {"name": "@vehicleId", "value": vehicleId}
            ],
            enable_cross_partition_query=True
        ))

        return func.HttpResponse(
            json.dumps(items),
            status_code=200
        )
    except (Exception,exceptions.CosmosHttpResponseError,JWTError) as e:
        return func.HttpResponse(
            body=str("Internal server error"),
            status_code=500
        )


@police_trigger.route(route="police/create-challan", auth_level=func.AuthLevel.ANONYMOUS,methods=["POST"])
def create_challan_by_vehicleId(req: func.HttpRequest) -> func.HttpResponse:
    try:
        token = req.headers.get('Authorization')
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        
        if not police_middleware(token):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        body = json.loads(req.get_body().decode('utf-8'))
        database = client.get_database_client(DATABASE_NAME)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

        vehicleId = body['vehicleId']
        amount = f"{body['amount']}"

        if(amount.isnumeric()):
            amount = int(amount)
            if(amount<0):
                return func.HttpResponse(
                    json.dumps("Amount can't be negative."),
                    status_code=404
                )
        else:
            return func.HttpResponse(
                json.dumps("Amount is not valid."),
                status_code=404
            )

        location = body['location']
        description = body['description']
        date = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        due_time = time.time()+3600*24*90
        status= "unsettled"
        settlement_date = ""

        get_vehicle_query = 'Select c.id,c.email from c where c.id = @vehicleId'
        vehicle = list(vehicle_container.query_items(query=get_vehicle_query,parameters=[
            {"name": "@vehicleId", "value": vehicleId}
        ],enable_cross_partition_query=True))


        if(len(vehicle) == 0):
            return func.HttpResponse(
                json.dumps("Vehicle id is not valid."),
                status_code=404
            )
        
        item = challan_container.create_item({
            "vehicleId": vehicleId,
            "amount": amount,
            "location": location,
            "description": description,
            "date": date,
            "due_time": due_time,
            "status": status,
            "settlement_date": settlement_date
        },enable_automatic_id_generation=True)
        email = vehicle[0]['email']

        subject = CHALLAN_SUBJECT.format(vehicleId)
        body = CHALLAN_BODY.format(vehicleId,amount,location,description)
        send_email(email,subject,body)
        logging.info("Challan Created Successfully")
        return func.HttpResponse(
            json.dumps("Created Challan Successfully"),
            status_code=201
        )
    except KeyError as e:
        logging.error(e)
        return func.HttpResponse(
            body=json.dumps("Invalid Body"),
            status_code=404
        )

    except (Exception,exceptions.CosmosHttpResponseError,JWTError) as e:
        logging.error(e)
        return func.HttpResponse(
            body=json.dumps("Internal server error"),
            status_code=500
        )
