import azure.functions as func
import json
from utils.db_connection import client
from utils.jwt_decode import encode_token, decode_token
from jose import JWTError
from azure.cosmos import  exceptions
import logging
import uuid
import datetime
import utils.send_email as email_service

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
        if(token.startswith('Bearer')):
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
    
@user_trigger.route('user/get-challan-by-vehicles/{vehicleId}',auth_level=func.AuthLevel.ANONYMOUS, methods=['GET'])
def get_vehicle_challans(req: func.HttpRequest)-> func.HttpResponse:
    try:
        logging.warn("Start")
        token = req.headers['Authorization']
        if(token.startswith('Bearer')):
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
            json.dumps(items),
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
        if(token.startswith('Bearer')):
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
            json.dumps(items),
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
        if(token.startswith('Bearer')):
            token = token.split(" ")[1]

        decoded_token = user_middleware(token)
        logging.warning("Heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeey")
        if not decoded_token:
            return func.HttpResponse(
                "Unauthorized",
                status_code=401
            )
        
        body = json.loads(req.get_body().decode('utf-8'))
        database = client.get_database_client(DATABASE_NAME)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)
        transaction_container = database.get_container_client(TRANSACTION_CONTAINER)

        logging.warning("Heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeey - 2")

        amount = int(body['amount'])
        # logging.warn(amount)
        tagid = req.route_params.get('tagid')   
        # logging.warning(tagid)
        if(amount<0):
            return func.HttpResponse(
                json.dumps({"msg":"Invalid amount"}),
                status_code=404
            )
        

        query = "SELECT * FROM c WHERE c.id = '{0}'".format(tagid)
        items = list(fastag_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        
        if len(items) == 0:
            return func.HttpResponse(
                json.dumps("Invalid Fastag"),
                status_code=200
            )
        
        if items[0]['email'] != decoded_token['email']:
            return func.HttpResponse(
                json.dumps("You are not authorized to recharge this fastag"),
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
            json.dumps("Invalid token"),
            status_code=404
        )
    except  exceptions.CosmosHttpResponseError as e:
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=500
        )
    except (JWTError, Exception) as e:
        logging.warn(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=500
        )
    
@user_trigger.route('user/get-transaction-history/{tagid}',auth_level=func.AuthLevel.ANONYMOUS, methods=['GET'])
def get_transaction_history(req:func.HttpRequest)-> func.HttpResponse:
    try:
        token = req.headers['Authorization']
        if(token.startswith('Bearer')):
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

@user_trigger.route('user/pay-all-challan/{vehicleId}',auth_level=func.AuthLevel.ANONYMOUS, methods=['POST'])
def pay_all_challan(req:func.HttpRequest)-> func.HttpResponse:
    try:
        logging.warn("Start")   
        token = req.headers['Authorization']
        if(token.startswith('Bearer')):
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

@user_trigger.route('user/pay-challan/{challanId}')
def pay_challan(req:func.HttpRequest)-> func.HttpResponse:
    try:
        pass
    except:
        pass

@user_trigger.route('user/send-alert',auth_level=func.AuthLevel.ANONYMOUS, methods=['POST'])
def send_alert(req:func.HttpRequest)-> func.HttpResponse:
    try:
        logging.warn("Alert Trigger Started")
        database = client.get_database_client(DATABASE_NAME)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

        query = 'SELECT DISTINCT c.vehicleId,c.amount FROM c WHERE c.status = "unsettled"'

        query_results = list(challan_container.query_items(query=query,enable_cross_partition_query=True))
        vehicle_to_challan = {}
        for result in query_results:
            try:
                vehicle_to_challan[result['vehicleId']]+=result['amount']
            except KeyError:
                vehicle_to_challan[result['vehicleId']]= result['amount']
            
        
        vehicleIds = tuple(vehicle_to_challan.keys())
        logging.warn(vehicleIds)
        query = 'SELECT c.email,c.id from c where c.id IN {0}'.format(vehicleIds)
        logging.warn(query)
        email_to_vehicleIds = list(vehicle_container.query_items(query=query, enable_cross_partition_query=True))

        vehicle_to_email_map = {}
        for email_to_vehicle in email_to_vehicleIds:
            vehicle_to_email_map[email_to_vehicle['id']]= email_to_vehicle['email']
        

        subject = "Pending Challans on your vehicle with vehicle number - {0}"
        body = """Hello Sir,\n
                You have pending challans on your vehicle with vehicle number {0}.\n
                Total Amount you have to pay is {1}.\n
                Log in to our portal for detail description of your challans and to pay your challans.\n
                If you won't pay your challans then your challans will be auto payed on your next toll visit.\n
                If your fastag won't have enough balance,then your fastag will be blacklisted"""

        for vehicle in vehicle_to_challan.keys():
            email = vehicle_to_email_map[vehicle]
            amount = vehicle_to_challan[vehicle]
            vehicleId = vehicle

            new_subject = subject.format(vehicleId)
            new_body = body.format(vehicleId,amount)
            email_service.send(email,new_subject,new_body)

        return func.HttpResponse(
            body=json.dumps("Success"),
            status_code=200
        )
    
    except exceptions.CosmosHttpResponseError as e:
        logging.warn("Testing")
        logging.warn(e)
        return func.HttpResponse(
            body=json.dumps({
                'Message':"Sending alert"
            })
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

