import azure.functions as func
import json
from azure.cosmos import  exceptions
from email_validator import validate_email,EmailNotValidError
from utils.db_connection import client
from utils.password import hash_password,check_password_strength,PASSWORD_CONSTRAINT,check_password
from utils.send_email import send_email
import logging

rto_triggers = func.Blueprint()

DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"
VEHICLE_CONTAINER = "Vehicle-Table"
FASTAG_CONTAINER = "Fastag-Table"

USER_CREATED_SUBJECT = "You are successfully registered"
USER_CREATED_BODY = """
Thank you for registering with us. You are successfully registered with us.<br>
Your login credentials are:<br>
    &nbsp;Email: {0}<br>
    &nbsp;Password: {1}<br>
You are designated as a {2}.<br>
Please login to the system to access the services.
"""

VEHICLE_ISSUED_SUBJECT = "Thank you for purchasing a vehicle and registering it"
VEHICLE_ISSUED_BODY = """
Hello {0},<br>
Thank you for purchasing a vehicle and registering it with us.<br>
Your vehicle is successfully registered with us.<br>
Your vehicle id is {1}.<br>
Your email id is {2}.<br>
Right now your vehicle does not have a fastag.<br>
You can purchase a fastag.<br>
Please use this id for any future reference.
"""

FASTAG_ISSUED_SUBJECT = "Thank you for purchasing a fastag"
FASTAG_ISSUED_BODY = """
Hello {0},<br>
Thank you for purchasing a fastag.<br>
Your fastag is successfully registered with us.<br>
Your fastag id is {1}.<br>
Your vehicle id is {2}.<br>
Your email id is {3}.<br>
Right now your fastag has a balance of Rs.{4}.<br>
You can use this fastag for any future toll payments.<br>
Please use this id for any future reference.
"""


@rto_triggers.route(route="rto/create-police-man",methods=["POST"])
def create_police_man(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.warning("Creating Police Man")
        body = json.loads(req.get_body().decode('utf-8'))
        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)
        name = body['name']
        designation = body['designation']
        password = body['password']
        email = body['email']
        logging.warning(f"Email: {email}")

        if designation != 'police':
            logging.error("Invalid Designation")
            return func.HttpResponse(
                json.dumps("Invalid Designation"),
                status_code=404
            )
        
        validate_email(email)

        if not check_password_strength(password):
            logging.error("Password Constraint")
            return func.HttpResponse(
                json.dumps(PASSWORD_CONSTRAINT),
                status_code=404
            )    

        query = "SELECT * FROM c WHERE c.email = '{0}' and c.designation='police'".format(email)
        items = list(user_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        if len(items) != 0:
            logging.error("User already exists")
            return func.HttpResponse(
                json.dumps("User already exists"),
                status_code=404
            )
        
        bcrypt_password = hash_password(password)

        user_container.create_item({
            "name": name,
            "designation": designation,
            "password": str(bcrypt_password),
            "email":email
        },enable_automatic_id_generation=True)
        send_email(email,USER_CREATED_SUBJECT,USER_CREATED_BODY.format(email,password,designation))
        logging.info("Successfully created police man user")
        return func.HttpResponse(
            json.dumps("Successfully created police man user"),
            status_code=201
        )
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

@rto_triggers.route(route="rto/create-toll-plaza-man",methods=["POST"])
def create_toll_plaza_man(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info("Toll plaza man triggered")
        body = json.loads(req.get_body().decode('utf-8'))
        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)

        name = body['name']
        designation = body['designation']
        password = body['password']
        email = body['email']

        logging.info(f"Email : {email}")

        if designation != 'toll':
            logging.error("Invalid Designation")
            return func.HttpResponse(
                json.dumps("Invalid Designation"),
                status_code=404
            )

        validate_email(email)
        if not check_password_strength(password):
            logging.error("Password constraint do not match")
            return func.HttpResponse(
                json.dumps(PASSWORD_CONSTRAINT),
                status_code=404
            )    

        query = "SELECT * FROM c WHERE c.email = '{0}' and c.designation='toll'".format(email)
        items = list(user_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        if len(items) != 0:
            logging.error("User already exists")
            return func.HttpResponse(
                json.dumps("User already exists"),
                status_code=404
            )

        bcrypt_password = hash_password(password)

        user_container.create_item({
            "name": name,
            "designation": designation,
            "password": bcrypt_password,
            "email":email
        },enable_automatic_id_generation=True)
        send_email(email,USER_CREATED_SUBJECT,USER_CREATED_BODY.format(email,password,designation))
        logging.info("Successfully created toll plaza user")
        return func.HttpResponse(
            json.dumps("Successfully created toll plaza user"),
            status_code=201
        )
    except EmailNotValidError:  
        logging.error("Invalid email")
        return func.HttpResponse(
            json.dumps("Invalid Email"),
            status_code=404
        )
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

@rto_triggers.route(route="rto/create-vehicle",methods=["POST"])
def create_vehicle(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info("Started with creating vehicle")
        body = json.loads(req.get_body().decode('utf-8'))

        database = client.get_database_client(DATABASE_NAME)
        user_container = database.get_container_client(USER_CONTAINER)
        vehicle_container = database.get_container_client(VEHICLE_CONTAINER)

        vehicle_id = body['vehicleId']
        email = body['email']
        name = body['name']
        designation = body['designation']
        password = body['password']

        logging.info(f"Email : {email}")

        if designation != 'user':
            logging.error("Invalid Designation")
            return func.HttpResponse(
                json.dumps("Invalid Designation"),
                status_code=404
            )

        validate_email(email)
   

        query = f"SELECT c.password FROM c WHERE c.email = '{email}' and c.designation = 'user'"
        get_user_by_email = list(user_container.query_items(query=query,enable_cross_partition_query=True))
        logging.warn(get_user_by_email)

        if len(get_user_by_email)>0 and (not check_password(password,get_user_by_email[0]['password'])):
            logging.error("User wants to issue a vehicle but enter wrong password while issuing vehicle.")
            return func.HttpResponse(
                json.dumps("User already exist with your email. Please enter correct password if you want to issue a new vehicle with the same vehicle id."),
                status_code=404
            )
        
        query = f"SELECT * FROM c WHERE c.id = '{vehicle_id}'"
        get_vehicle_by_id = list(vehicle_container.query_items(query=query,enable_cross_partition_query=True))

        if len(get_vehicle_by_id) != 0:
            logging.error("Vehicle Id already exist")
            return func.HttpResponse(
                json.dumps("Vehicle Id already exists"),
                status_code=404
            )

        if len(get_user_by_email) == 0:
            bcrypt_password = hash_password(password)
            user_entry= {
                "name": name,
                "designation": designation,
                "password": bcrypt_password,
                "email":email
            }
            user_container.create_item(user_entry,enable_automatic_id_generation=True)
            send_email(email,USER_CREATED_SUBJECT,USER_CREATED_BODY.format(email,password,designation))
        logging.warning("Started creating vehicle")
        vehicle_entry={
            "id": vehicle_id,
            "email": email,
            "tagId":""
        }
        vehicle_container.create_item(vehicle_entry)
        send_email(email,VEHICLE_ISSUED_SUBJECT,VEHICLE_ISSUED_BODY.format(name,vehicle_id,email))
        logging.info("Successfully issued vehicle.")
        return func.HttpResponse(
            json.dumps("Successfully created vehicle"),
            status_code=201
        )
    except EmailNotValidError:  
        logging.error("Invalid Email")
        return func.HttpResponse(
            json.dumps("Invalid Email"),
            status_code=404
        )
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
        logging.info("Starting with associating Fastag")
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
            logging.error("No vehicle exist with this id.")
            return func.HttpResponse(
                json.dumps("Your vehicle id is not valid"),
                status_code=404
            )
        current_tagid = get_vehicle_by_id[0]['tagId']
        if current_tagid != "":
            logging.error("Vehicle is already associated with a fastag.")
            return func.HttpResponse(
                json.dumps("Your vehicle already has a fastag"),
                status_code=404
            )
        
        query = f"SELECT * FROM c WHERE c.id = '{tagid}'"
        get_fastag_by_id = list(fastag_container.query_items(query=query,enable_cross_partition_query=True))
        if len(get_fastag_by_id) != 0:
            return func.HttpResponse(
                json.dumps("Fastag id already exists"),
                status_code=404
            )
        email = get_vehicle_by_id[0]['email']
        vehicle_container.upsert_item(body= {
            "id": vehicleId,
            "email": email,
            "tagId":tagid
        })
        fastag_container.create_item({
            "id": tagid,
            "balance": balance,
            "status": status,
            "vehicleId": vehicleId,
            "email": get_vehicle_by_id[0]['email']
        })
        send_email(email,FASTAG_ISSUED_SUBJECT,FASTAG_ISSUED_BODY.format(email,tagid,vehicleId,email,balance))
        logging.info("Successfully created fastag and associated it with fastag.")
        return func.HttpResponse(
            json.dumps("Successfully created fastag"),
            status_code=201
        )
    except KeyError:
        logging.error("Invalid body")
        return func.HttpResponse(
            json.dumps("Invalid body"),
            status_code=404
        )
    except (exceptions.CosmosHttpResponseError,exceptions.CosmosResourceExistsError,Exception) as e:
        logging.error(e)
        return func.HttpResponse(
            json.dumps("Internal Server Error"),
            status_code=501
        )

