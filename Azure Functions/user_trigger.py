import azure.functions as func
import json
from utils.db_connection import client
from utils.jwt_decode import encode_token, decode_token
from jose import JWTError
from azure.cosmos import  exceptions
import logging
import time
import datetime
from utils.password import check_password

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
        if data['exp']<time.time():
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

        query = "SELECT c.id,c.password FROM c WHERE c.email = '{0}' and c.designation = 'user'".format(email)
        items = list(user_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        if len(items) == 0:
            return func.HttpResponse(
                json.dumps("Invalid Email or Password"),
                status_code=404
            )
        user_password = items[0]['password']
        logging.warning(user_password)
        if not check_password(password,user_password):
            logging.error("Wrong password")
            return func.HttpResponse(
                json.dumps("Invalid email or password"),
                status_code=404
            )

        token = encode_token({
            "email":email,
            "designation":'user',
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
            json.dumps("Invalid body"),
            status_code=404
        )
    except  (exceptions.CosmosHttpResponseError,JWTError, Exception) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
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
                json.dumps("Unauthorized"),
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
                json.dumps("No Vehicles found"),
                status_code=404
            )
        return func.HttpResponse(
            body=json.dumps(items),
            status_code=200
        )
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except  (exceptions.CosmosHttpResponseError,JWTError, Exception) as e:
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
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
                json.dumps("Unauthorized"),
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
                json.dumps("You are not authorized to view this"),
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
                json.dumps("No Challans found"),
                status_code=404
            )
        
        return func.HttpResponse(
            json.dumps(items),
            status_code=200
        )
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except  (exceptions.CosmosHttpResponseError,JWTError, Exception) as e:
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
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
                json.dumps("Unauthorized"),
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
                json.dumps("No Fastags found"),
                status_code=404
            )
        return func.HttpResponse(
            json.dumps(items),
            status_code=200
        )
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except  (exceptions.CosmosHttpResponseError  ,JWTError, Exception) as e:
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=500
        )
    
@user_trigger.route('user/recharge-fastag/{tagid}',auth_level=func.AuthLevel.ANONYMOUS, methods=['POST'])
def recharge_fastags(req: func.HttpRequest)-> func.HttpResponse:
    try:
        token = req.headers['Authorization']
        if(token.startswith('Bearer')):
            token = token.split(" ")[1]

        decoded_token = user_middleware(token)
        if not decoded_token:
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        
        body = json.loads(req.get_body().decode('utf-8'))
        database = client.get_database_client(DATABASE_NAME)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)
        transaction_container = database.get_container_client(TRANSACTION_CONTAINER)

        amount = f"{body['amount']}"
        tagid = req.route_params.get('tagid')   

        if(tagid==""):
            return func.HttpResponse(
                json.dumps("Invalid Fastag"),
                status_code=404
            )

        if not amount.isnumeric():
            return func.HttpResponse(
                json.dumps("Invalid amount entered"),
                status_code=404
            ) 
        amount =int(amount)
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
                status_code=404
            )
        
        if items[0]['email'] != decoded_token['email']:
            return func.HttpResponse(
                json.dumps("You are not authorized to recharge this fastag"),
                status_code=401
            )
        if items[0]['status'] != 'valid':
            return func.HttpResponse(
                json.dumps("Your card is blacklisted. Please visit nearby RTO office and settle your dues."),
                status_code=404
            )
        items[0]['balance'] = int(items[0]['balance']) + amount

        fastag_container.upsert_item(items[0])

        timestamp = str(datetime.datetime.now())
        tid = tagid
        amount = amount
        type_of_transaction ="credit"
        description = "Recharge"

        transaction_container.create_item({
            "timestamp":timestamp,
            "tagId":tid,
            "amount":amount,
            "type":type_of_transaction,
            "description":description
        },enable_automatic_id_generation=True)
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
    except  (exceptions.CosmosHttpResponseError,JWTError, Exception) as e:
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
                json.dumps("Unauthorized"),
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
                json.dumps("Invalid Fastag"),
                status_code=404
            )
        
        if items[0]['email'] != email:
            return func.HttpResponse(
                json.dumps("You are not authorized to view this"),
                status_code=401
            )
        
        query = "SELECT * FROM c WHERE c.tagId = '{0}'".format(tagid)
        items = list(transaction_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        if len(items) == 0:
            return func.HttpResponse(
                json.dumps("No Transactions found"),
                status_code=404
            )

        return func.HttpResponse(
            body=json.dumps(items),
            status_code=200
        )
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except (JWTError, Exception,exceptions.CosmosHttpResponseError) as e:
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=500
        )

@user_trigger.route('user/pay-a-challan/{challanId}',auth_level=func.AuthLevel.ANONYMOUS,methods=["POST"])
def pay_single_challan(req:func.HttpRequest)-> func.HttpResponse:
    try:
        token = req.headers['Authorization']
        if(token.startswith('Bearer')):
            token = token.split(" ")[1]
        decoded_token = user_middleware(token)

        if not decoded_token:
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        user_email = decoded_token['email']
        logging.warning("Pay a single challan")
        
        database = client.get_database_client(DATABASE_NAME)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)
        transaction_container = database.get_container_client(TRANSACTION_CONTAINER)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

        challanId = req.route_params.get('challanId')

        challan_query = 'Select * from c where c.id = "{0}"'.format(challanId)
        challan_item = list(challan_container.query_items(query=challan_query,enable_cross_partition_query=True))

        if len(challan_item) == 0:
            return func.HttpResponse(
                json.dumps("Invalid challan id"),
                status_code=404
            )
        
        if challan_item[0]['status'] != 'unsettled':
            return func.HttpResponse(
                json.dumps("You have already paid this challan"),
                status_code=404
            )
        

        
        vehicleId = challan_item[0]['vehicleId']
        challan_amount = challan_item[0]['amount']

        query = 'Select * from c where c.id = "{0}" and c.email="{1}"'.format(vehicleId,user_email)
        check_vehicle_association = list(vehicle_container.query_items(query=query,enable_cross_partition_query=True))

        if len(check_vehicle_association)==0:
            return func.HttpResponse(
                json.dumps("You are not associated with this vehicle"),
                status_code=404
            )
        logging.warn("You are associated with this vehicle")
        fastag_query = 'Select * from c where c.vehicleId = "{0}"'.format(vehicleId)
        fastag_info = list(fastag_container.query_items(query=fastag_query,enable_cross_partition_query=True))

        if len(fastag_info)==0:
            return func.HttpResponse(
                json.dumps("No fastag associated with the vehicle."),
                status_code=404
            )
        
        if fastag_info[0]['status']!='valid':
            return func.HttpResponse(
                json.dumps("Your fastag is blacklisted. Visit nearby RTO office to settle your dues."),
                status_code=404
            )

        fastag_balance = int(fastag_info[0]['balance'])

        if fastag_balance<challan_amount:
            return func.HttpResponse(
                json.dumps("Associated fastag do not have enough balance. Please recharge it."),
                status_code=404
            )
        
        fastag_info[0]['balance']= int(fastag_info[0]['balance'])- int(challan_amount)
        fastag_container.upsert_item(fastag_info[0])

        challan_item[0]['status']= 'settled'
        challan_item[0]['settlement_date'] = str(datetime.datetime.now())
        challan_container.upsert_item(challan_item[0])

        transaction_container.create_item({
                "timestamp":str(datetime.datetime.now()),
                "tagId":fastag_info[0]['id'],
                "amount":challan_item[0]['amount'],
                "type":'debit',
                "description":'Challan Payment'
        },enable_automatic_id_generation=True)
        return func.HttpResponse(
            json.dumps("Challan payed successfully"),
            status_code=200
        )
    except (exceptions.CosmosHttpResponseError,Exception,JWTError) as e:
        logging.warning(e)
        return func.HttpResponse(
            json.dumps("Something went wrong"),
            status_code=404
        )

@user_trigger.route('user/pay-all-challan/{vehicleId}',auth_level=func.AuthLevel.ANONYMOUS, methods=['POST'])
def pay_all_challan(req:func.HttpRequest)-> func.HttpResponse:
    try:
        token = req.headers['Authorization']
        if(token.startswith('Bearer')):
            token = token.split(" ")[1]
        decoded_token = user_middleware(token)

        if not decoded_token:
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        
        user_email = decoded_token['email']

        database = client.get_database_client(DATABASE_NAME)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)
        transaction_container = database.get_container_client(TRANSACTION_CONTAINER)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

        vehicleId = req.route_params.get('vehicleId')

        query = 'Select * from c where c.id = "{0}" and c.email="{1}"'.format(vehicleId,user_email)
        check_vehicle_association = list(vehicle_container.query_items(query=query,enable_cross_partition_query=True))

        if len(check_vehicle_association)==0:
            return func.HttpResponse(
                json.dumps("You are not associated with this vehicle"),
                status_code=404
            )

        query = 'SELECT * FROM c WHERE c.vehicleId = "{0}" and c.status = "unsettled" '.format(vehicleId)
        challan_items = list(challan_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        logging.error(challan_items)

        if len(challan_items) == 0:
            return func.HttpResponse(
                json.dumps("No Challans found"),
                status_code=404
            )
    
        amount = 0
        for item in challan_items:
            amount+= int(item['amount'])

        logging.error(amount)

        query = "SELECT * FROM c WHERE c.vehicleId = '{0}'".format(vehicleId)
        items = list(fastag_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        if len(items) == 0:
            return func.HttpResponse(
                json.dumps("No Fastag found"),
                status_code=404
            )
        
        if items[0]['status']!='valid':
            return func.HttpResponse(
                json.dumps("Your fastag is blacklisted. Visit nearby RTO office to settle your dues."),
                status_code=404
            )
    
        logging.warning(items[0]['balance'])
        logging.warning(amount)

        if int(items[0]['balance']) < amount:
            logging.warning(items[0]['balance'])
            logging.warning(amount)
            return func.HttpResponse(
                json.dumps("Insufficient Balance"),
                status_code=404
            )
        tagId = items[0]['id']
        items[0]['balance'] = int(items[0]['balance']) - amount
        fastag_container.upsert_item(items[0])

        for item in challan_items:
            item['status'] = "settled"
            item['settlement_date'] = str(datetime.datetime.now())
            challan_container.upsert_item(item)
            timestamp = str(datetime.datetime.now())
            amount = item['amount']
            type_of_transaction ="debit"
            description = "Challan Payment"

            transaction_container.create_item({
                "timestamp":timestamp,
                "tagId":tagId,
                "amount":amount,
                "type":type_of_transaction,
                "description":description
            },enable_automatic_id_generation=True)

        return func.HttpResponse(
            body=json.dumps({
                "message":"Challan Payment Successful",
            }),
            status_code=200
        )

    except KeyError as e:
        logging.warning(e)
        return func.HttpResponse(
            json.dumps("Invalid token"),
            status_code=404
        )
    except  (exceptions.CosmosHttpResponseError,JWTError, Exception) as e:
        logging.warning(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=500
        )


