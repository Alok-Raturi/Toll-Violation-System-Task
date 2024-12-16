import azure.functions as func
import json
from utils.db_connection import client
from utils.jwt_decode import encode_token, decode_token
from jose import JWTError
from azure.cosmos import  exceptions
import logging
import uuid
import datetime

DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"
VEHICLE_CONTAINER = "Vehicle-Table"
CHALLAN_CONTAINER = "Challan-Table"
FASTAG_CONTAINER = "Fastag-Table"
TRANSACTION_CONTAINER = "Transaction-Table"

user_trigger = func.Blueprint()

def user_middleware(token:str):
    try:
        logging.warn(token)
        data = decode_token(token)
        if data['designation'] != "user":
            return False
        return data
    except JWTError:
        return False

@user_trigger.route('user/login',auth_level=func.AuthLevel.ANONYMOUS, methods=['POST'])
def login_user(req: func.HttpRequest)->func.HttpResponse:
    try:
        body = json.loads(req.get_body().decode('utf-8'))
        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)

        email = body['email']
        password = body['password']

        query = "SELECT * FROM c WHERE c.email = '{0}' and c.password = '{1}' and c.designation = 'user'".format(email,password)
        items = list(user_container.query_items(
            query=query,
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
                body=json.dumps({
                    "access_token":token
                }),
                status_code=200
            )
    except KeyError:
        return func.HttpResponse(
            "Invalid body",
            status_code=404
        )
    except  (exceptions.CosmosHttpResponseError) as e:
        return func.HttpResponse(
            "Internal Server Error",
            status_code=500
        )
    except (JWTError, Exception) as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )

@user_trigger.route('user/get-vehicles',auth_level=func.AuthLevel.ANONYMOUS, methods=['GET'])
def get_vehicles(req: func.HttpRequest)->func.HttpResponse:
    try:
        token = req.headers['Authorization']
        token = token.split(" ")[1]
        if not user_middleware(token):
            return func.HttpResponse(
                "Unauthorized",
                status_code=401
            )
        database = client.get_database_client(DATABASE_NAME)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

        email = decode_token(token)['email']
        logging.warn(email)
        query = "SELECT * FROM c WHERE c.email = '{0}'".format(email)
        items = list(vehicle_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        if len(items) == 0:
            return func.HttpResponse(
                "No Vehicles found",
                status_code=200
            )
        return func.HttpResponse(
            body=json.dumps(items),
            status_code=200
        )
    except KeyError:
        return func.HttpResponse(
            "Invalid token",
            status_code=404
        )
    except  exceptions as e:
        return func.HttpResponse(
            "Internal Server Error",
            status_code=500
        )
    except (JWTError, Exception) as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )
    
@user_trigger.route('user/get-challan-by-vehicles/{vehicleId}',auth_level=func.AuthLevel.ANONYMOUS, methods=['GET'])
def get_vehicle_challans(req: func.HttpRequest)-> func.HttpResponse:
    try:
        logging.warn("Start")
        token = req.headers['Authorization']
        token = token.split(" ")[1]

        decoded_token = user_middleware(token)
        if not decoded_token:
            logging.warn("Done")
            return func.HttpResponse(
                "Unauthorized",
                status_code=401
            )
        logging.warn(decoded_token)
        database = client.get_database_client(DATABASE_NAME)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)
        
        
        email = decoded_token['email']
        vehicleId = req.route_params.get('vehicleId')
        get_email = 'Select c.email from c where c.id = "{0}"'.format(vehicleId)   
        email_item = list(vehicle_container.query_items(
            query=get_email,
            enable_cross_partition_query=True
        ))
        if(email != email_item[0]['email']):
            return func.HttpResponse(
                "You are not authorized to view this",
                status_code=401
            )
        
        query = "SELECT * FROM c WHERE c.vehicleId = '{0}'".format(vehicleId)
        items = list(challan_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        logging.warn(items)
        if len(items) == 0:
            return func.HttpResponse(
                "No Challans found",
                status_code=200
            )
        
        return func.HttpResponse(
            str(items),
            status_code=200
        )
    except KeyError:
        return func.HttpResponse(
            "Invalid token",
            status_code=404
        )
    except  exceptions.CosmosHttpResponseError as e:
        return func.HttpResponse(
            "Internal Server Error",
            status_code=500
        )
    except (JWTError, Exception) as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )
    
@user_trigger.route('user/get-fastags',auth_level=func.AuthLevel.ANONYMOUS, methods=['GET'])
def get_fastags(req:func.HttpRequest)-> func.HttpResponse:
    try:
        token = req.headers['Authorization']
        token = token.split(" ")[1]
        decoded_token = user_middleware(token)
        if not decoded_token:
            return func.HttpResponse(
                "Unauthorized",
                status_code=401
            )
        database = client.get_database_client(DATABASE_NAME)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)

        email = decoded_token['email']
        query = "SELECT * FROM c WHERE c.email = '{0}'".format(email)
        items = list(fastag_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        if len(items) == 0:
            return func.HttpResponse(
                "No Fastags found",
                status_code=200
            )
        return func.HttpResponse(
            str(items),
            status_code=200
        )
    except KeyError:
        return func.HttpResponse(
            "Invalid token",
            status_code=404
        )
    except  exceptions.CosmosHttpResponseError as e:
        return func.HttpResponse(
            "Internal Server Error",
            status_code=500
        )
    except (JWTError, Exception) as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )
    
@user_trigger.route('user/recharge-fastag/{tagid}',auth_level=func.AuthLevel.ANONYMOUS, methods=['POST'])
def recharge_fastags(req: func.HttpRequest)-> func.HttpResponse:
    try:
        token = req.headers['Authorization']
        token = token.split(" ")[1]
        decoded_token = user_middleware(token)

        if not decoded_token:
            return func.HttpResponse(
                "Unauthorized",
                status_code=401
            )
        
        body = json.loads(req.get_body().decode('utf-8'))
        database = client.get_database_client(DATABASE_NAME)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)
        transaction_container = database.get_container_client(TRANSACTION_CONTAINER)

        amount = int(body['amount'])
        tagid = req.route_params.get('tagid')   

        if(amount<0):
            return func.HttpResponse(
                "Invalid amount",
                status_code=404
            )
        
        query = "SELECT * FROM c WHERE c.id = '{0}'".format(tagid)
        items = list(fastag_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        if len(items) == 0:
            return func.HttpResponse(
                "Invalid Fastag",
                status_code=200
            )
        
        if items[0]['email'] != decoded_token['email']:
            return func.HttpResponse(
                "You are not authorized to recharge this fastag",
                status_code=401
            )
        items[0]['balance'] = str(int(items[0]['balance']) + amount)

        fastag_container.upsert_item(items[0])

        transaction_id = uuid.uuid4()
        timestamp = str(datetime.datetime.now())
        tid = tagid
        amount = amount
        type_of_transaction ="credit"
        description = "Recharge"

        transaction_container.create_item({
            "id":str(transaction_id),
            "timestamp":timestamp,
            "tagId":tid,
            "amount":amount,
            "type":type_of_transaction,
            "description":description
        })
        return func.HttpResponse(
            body=json.dumps({
                "message":"Recharge Successful",
                "balance":items[0]['balance']
            }),
            status_code=200
        )
    except KeyError:
        return func.HttpResponse(
            "Invalid token",
            status_code=404
        )
    except  exceptions.CosmosHttpResponseError as e:
        return func.HttpResponse(
            "Internal Server Error",
            status_code=500
        )
    except (JWTError, Exception) as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )
    
@user_trigger.route('user/get-transaction-history/{tagid}',auth_level=func.AuthLevel.ANONYMOUS, methods=['GET'])
def get_transaction_history(req:func.HttpRequest)-> func.HttpResponse:
    try:
        token = req.headers['Authorization']
        token = token.split(" ")[1]
        decoded_token = user_middleware(token)

        if not decoded_token:
            return func.HttpResponse(
                "Unauthorized",
                status_code=401
            )
        
        database = client.get_database_client(DATABASE_NAME)
        transaction_container = database.get_container_client(TRANSACTION_CONTAINER)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)

        email = decoded_token['email']
        tagid = req.route_params.get('tagid')
        query = "SELECT * FROM c WHERE c.id = '{0}'".format(tagid)
        items = list(fastag_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        if len(items) == 0:
            return func.HttpResponse(
                "Invalid Fastag",
                status_code=200
            )
        
        if items[0]['email'] != email:
            return func.HttpResponse(
                "You are not authorized to view this",
                status_code=401
            )
        
        query = "SELECT * FROM c WHERE c.tagId = '{0}'".format(tagid)
        items = list(transaction_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        if len(items) == 0:
            return func.HttpResponse(
                "No Transactions found",
                status_code=200
            )

        return func.HttpResponse(
            body=json.dumps(items),
            status_code=200
        )
    except KeyError:
        return func.HttpResponse(
            "Invalid token",
            status_code=404
        )
    except  exceptions.CosmosHttpResponseError as e:
        return func.HttpResponse(
            "Internal Server Error",
            status_code=500
        )
    except (JWTError, Exception) as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )

@user_trigger.route('user/pay-challan/{vehicleId}',auth_level=func.AuthLevel.ANONYMOUS, methods=['POST'])
def pay_challan(req:func.HttpRequest)-> func.HttpResponse:
    try:
        logging.warn("Start")   
        token = req.headers['Authorization']
        token = token.split(" ")[1]
        decoded_token = user_middleware(token)

        if not decoded_token:
            return func.HttpResponse(
                "Unauthorized",
                status_code=401
            )
        logging.warn("Starting")   
        
        database = client.get_database_client(DATABASE_NAME)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)
        transaction_container = database.get_container_client(TRANSACTION_CONTAINER)

        vehicleId = req.route_params.get('vehicleId')
        logging.warn(vehicleId)
        query = 'SELECT VALUE SUM(c.amount) FROM c WHERE c.vehicleId = "{0}" and c.status = "unsettled" '.format(vehicleId)
        logging.warn(query)
        items = list(challan_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        if len(items) == 0:
            return func.HttpResponse(
                "No Challans found",
                status_code=200
            )
    

        amount = int(items[0])
        logging.warn(amount)

        # Check associated Fastag
        query = "SELECT * FROM c WHERE c.vehicleId = '{0}'".format(vehicleId)
        items = list(fastag_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        if len(items) == 0:
            return func.HttpResponse(
                "No Fastag found",
                status_code=200
            )
    
        if int(items[0]['balance']) < amount:
            return func.HttpResponse(
                "Insufficient Balance",
                status_code=200
            )
        
        items[0]['balance'] = str(int(items[0]['balance']) - amount)
        fastag_container.upsert_item(items[0])

        query = 'SELECT * FROM c WHERE c.vehicleId = "{0}" and c.status = "unsettled" '.format(vehicleId)
        items = list(challan_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        for item in items:
            item['status'] = "settled"
            challan_container.upsert_item(item)
            transaction_id = uuid.uuid4()
            timestamp = str(datetime.datetime.now())
            tid = item['id']
            amount = item['amount']
            type_of_transaction ="debit"
            description = "Challan Payment"

            transaction_container.create_item({
                "id":str(transaction_id),
                "timestamp":timestamp,
                "tagId":tid,
                "amount":amount,
                "type":type_of_transaction,
                "description":description
            })

        return func.HttpResponse(
            body=json.dumps({
                "message":"Challan Payment Successful",
            }),
            status_code=200
        )

    except KeyError:
        return func.HttpResponse(
            "Invalid token",
            status_code=404
        )
    except  exceptions.CosmosHttpResponseError as e:
        return func.HttpResponse(
            "Internal Server Error",
            status_code=500
        )
    except (JWTError, Exception) as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )

# Pay all challan - Done
# Fastag Information - Done
# Recharge Fastag - Done
# Transaction History - Done

# RSA for jwt token - Done
# RTO -CLI based project
# Police - CLI based project
# version.tf and variables.tf
# Change your password