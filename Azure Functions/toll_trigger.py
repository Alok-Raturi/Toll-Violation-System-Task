import azure.functions as func
import json
from utils.db_connection import client
from utils.jwt_decode import encode_token, decode_token
from utils.transactions import update_fastag_balance, create_transaction
from utils.challans import settle_overdue_challans, fetch_overdue_challan, total_overdue_challans
from jose import JWTError
from azure.cosmos import exceptions
import logging
from utils.password import check_password

toll_trigger = func.Blueprint()

DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"
VEHICLE_CONTAINER = "Vehicle-Table"
CHALLAN_CONTAINER = "Challan-Table"
FASTAG_CONTAINER = "Fastag-Table"
TRANSACTION_CONTAINER = "Transaction-Table"


# Validating Designation
def toll_middleware(token: str):
    try:
        data = decode_token(token)
        if data['designation'] != "toll":
            return False
        return True
    except JWTError or KeyError:
        return False


# Fetch and validate access token from request
def validate_token(req: func.HttpRequest) -> bool:
    token = req.headers.get('Authorization')
    if token.startswith("Bearer "):
        token = token.split(" ")[1]
    # logging.warn(token)
    return toll_middleware(token)


# Validate Vehicle id
def validate_vehicle_id(database, vehicle_id) -> bool:
    vehicle_container = database.get_container_client(VEHICLE_CONTAINER)
    query = "SELECT * FROM c WHERE c.id = @vehicleId"
    items = list(vehicle_container.query_items(
        query= query,
        parameters=[
            {"name":"@vehicleId","value":vehicle_id}
        ],
        enable_cross_partition_query=True
    ))
    if len(items) == 0:
        return False
    return True    


# Blacklist Fastag
def blacklist_fastag(database, tag_id, vehicle_id):
    fastag_container = database.get_container_client(FASTAG_CONTAINER)
    operations = [
        {"op": "replace", "path": "/status", "value": "invalid"}
    ]
    fastag_container.patch_item(
        item=tag_id,
        patch_operations = operations,
        partition_key = vehicle_id
    )


# Get Tag Id from vehicle id
def get_tag_id_from_vehicle_id(database, vehicle_id):
    vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

    query = "SELECT c.tagId FROM c WHERE c.id = @vehicleId"
    items = list(vehicle_container.query_items(
        query=query,
        parameters=[
            {"name": "@vehicleId", "value": vehicle_id}
        ],
        enable_cross_partition_query=True
    ))
    logging.warn(items)
    if items[0]['tagId'] == '':
        return ''
    else:
        return items[0]['tagId']    


# Login
@toll_trigger.route(route = "toll/login", methods = ["POST"])
def toll_login(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = json.loads(req.get_body().decode('utf-8'))

        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)
        email = body['email']
        password = body['password']

        query = "SELECT * FROM c WHERE c.email = '{0}' and c.designation = 'toll'".format(email, password)
        items = list(user_container.query_items(
            query = query,
            enable_cross_partition_query = True
        ))

        if len(items) == 0 or check_password(password,items[0]['password']):
            return func.HttpResponse(
                json.dumps("Invalid Email or Password"),
                status_code = 404
            )

        token = encode_token({
            "email" : email,
            "designation" : items[0]['designation'], 
            "id": items[0]['id']
        })    
        return func.HttpResponse(
            json.dumps({
                "access_token" : token
            }),
            status_code = 200
        )
    except KeyError:
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code = 404
        )
    except (JWTError, Exception,exceptions.CosmosHttpResponseError) as e:
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=500
        )


# View Challans by vehicle id
@toll_trigger.route(route="toll/get-challan/{vehicleId}", methods=["GET"])
def get_challan(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if not validate_token(req):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        
        vehicle_id = req.route_params.get('vehicleId')

        database = client.get_database_client(DATABASE_NAME)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)
        
        if not validate_vehicle_id(database, vehicle_id):
            return func.HttpResponse(
                json.dumps("Invalid vehicle Id"),
                status_code=404
            )

        query = "SELECT * FROM c WHERE c.vehicleId = @vehicleId"
        items = list(challan_container.query_items(
            query=query,
            parameters=[
                {"name": "@vehicleId", "value": vehicle_id}
            ],
            enable_cross_partition_query=True
        ))

        if(len(items)==0):
            return func.HttpResponse(
                json.dumps("No Overdue Challan for this vehicle"),
                status_code=200
            )

        return func.HttpResponse(
            json.dumps(items),
            status_code=200
        )
    except (Exception,exceptions.CosmosHttpResponseError) as e:
        return func.HttpResponse(
            json.dumps("Internal server error"),
            status_code=500
        )


# View fastag balance by tagid
@toll_trigger.route(route="toll/get-balance/{tagId}", methods=["GET"])
def get_balance(req: func.HttpRequest) -> func.HttpResponse:
    try:
        if not validate_token(req):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )
        tag_id = req.route_params.get('tagId')

        database = client.get_database_client(DATABASE_NAME)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)

        query = "SELECT c.balance FROM c WHERE c.id = @tagId"
        items = list(fastag_container.query_items(
            query=query,
            parameters=[
                {"name": "@tagId", "value": tag_id}
            ],
            enable_cross_partition_query=True
        ))

        if(len(items)==0):
            return func.HttpResponse(
                json.dumps("Invalid Fastag Id"),
                status_code=404
            )

        return func.HttpResponse(
            json.dumps(items[0]),
            status_code=200
        )
    except (Exception,exceptions.CosmosHttpResponseError) as e:
        return func.HttpResponse(
            json.dumps("Internal server error"),
            status_code=500
        )


# Settle due date passed challans, and blacklist fastag if low balance (Change tag status and balance, update transaction table)
@toll_trigger.route(route="toll/settle-overdue-challans/{vehicleId}", methods=["POST"])
def settle_overdue_challans_trigger(req: func.HttpRequest) -> func.HttpResponse:
    try:
        vehicle_id = req.route_params.get('vehicleId')
        body = json.loads(req.get_body().decode('utf-8'))
        passage_amount = body['passage-amount']

        if not passage_amount.isnumeric():
            return func.HttpResponse(
                json.dumps("Passage amount is not valid."),
                status_code=404
            )    
        passage_amount = int(passage_amount)

        if not validate_token(req):
            return func.HttpResponse(
                json.dumps("Unauthorized"),
                status_code=401
            )

        logging.warn('Token validated')
        database = client.get_database_client(DATABASE_NAME)
        if not validate_vehicle_id(database, vehicle_id):
            return func.HttpResponse(
                json.dumps("Invalid vehicle Id"),
                status_code=404
            )
            
        logging.warn('Vehicle validated')
        tag_id = get_tag_id_from_vehicle_id(database, vehicle_id)

        # logging.warn("Tag id fetched")
        if tag_id == '':
            return func.HttpResponse(
                json.dumps("No Fastag issued for the vehicle. Issue a Fastag first" ),
                status_code=404
            )

        logging.warn("Tag id fetched")
        fastag_container = database.get_container_client(FASTAG_CONTAINER)
        query = "SELECT c.balance FROM c WHERE c.id = @tagId"
        items = list(fastag_container.query_items(
            query=query,
            parameters=[
                {"name": "@tagId", "value": tag_id}
            ],
            enable_cross_partition_query=True
        ))

        if(len(items)==0):
            return func.HttpResponse(
                json.dumps("Invalid Fastag Id"),
                status_code=404
            ) 
        logging.warn(items)
        logging.warn("Remaining Balance Fetched")

        remaining_balance = items[0]['balance']   # Fetched remaining balance
        logging.warn(remaining_balance)

        # Fetching overdue challans
        overdue_challans = fetch_overdue_challan(vehicle_id)
        if not overdue_challans:
            return func.HttpResponse(
                json.dumps("Internal server error"),
                status_code= 500
            )
        # No challan: Deduct passage amount and pass
        if len(overdue_challans) == 0:
            if remaining_balance >= passage_amount:
                create_transaction(tag_id= tag_id, type= 'debit', amount= passage_amount, description= 'Toll Plaza Passage')
                update_fastag_balance(tag_id= tag_id, vehicle_id= vehicle_id, updated_balance= remaining_balance - passage_amount)
                return func.HttpResponse(
                    json.dumps("Passage Granted"),
                    status_code = 200
                )
            else:
                return func.HttpResponse(
                    json.dumps("Passage Blocked!!!  Insufficient Balance for passage"),
                    status_code = 404                
                )

        overdue_challans_amount = total_overdue_challans(overdue_challans) 
        logging.warn(overdue_challans_amount)

        if remaining_balance >= overdue_challans_amount + passage_amount:
            # Deduct total amount, change challans status and pass
            logging.warn("case 1")

            if not settle_overdue_challans(overdue_challans, vehicle_id, tag_id, remaining_balance - overdue_challans_amount):
                return func.HttpResponse(
                    json.dumps("Internal server error!! Can't settle challans"),
                    status_code=500
                ) 
            create_transaction(tag_id= tag_id, type= 'debit', amount= passage_amount, description= 'Toll Plaza Passage')
            update_fastag_balance(tag_id= tag_id, vehicle_id= vehicle_id, updated_balance= remaining_balance - passage_amount)
            return func.HttpResponse(
                json.dumps("Passage Granted, paid overdue challans"),
                status_code = 200
            )

        elif remaining_balance >= passage_amount:
            # Deduct passage amount, block fastag and pass
            logging.warn("case 2")
            create_transaction(tag_id= tag_id, type= 'debit', amount= passage_amount, description= 'Toll Plaza Passage')
            update_fastag_balance(tag_id= tag_id, vehicle_id= vehicle_id, updated_balance= remaining_balance - passage_amount)    

            blacklist_fastag(database=database, tag_id=tag_id, vehicle_id=vehicle_id)
            return func.HttpResponse(
                json.dumps("Passage Granted but Fastag blacklisted as insufficient balance for overdue challans"),
                status_code = 200
            )
        else: 
            # Block fastag and don't pass
            logging.warn("case 3")
            blacklist_fastag(database=database, tag_id=tag_id, vehicle_id=vehicle_id)
            return func.HttpResponse(
                json.dumps("Passage Blocked!!! and Fastag blacklisted as insufficient balance for passage and overdue challans"),
                status_code= 404
            )
    except (Exception,exceptions.CosmosHttpResponseError) as e:
        logging.warning(e)
        return func.HttpResponse(
            json.dumps("Internal server error"),
            status_code=500
        )    


 

    