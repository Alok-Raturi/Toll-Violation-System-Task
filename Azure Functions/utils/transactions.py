from utils.db_connection import client
from azure.cosmos import  exceptions
import datetime
import logging


DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"
VEHICLE_CONTAINER = "Vehicle-Table"
CHALLAN_CONTAINER = "Challan-Table"
FASTAG_CONTAINER = "Fastag-Table"
TRANSACTION_CONTAINER = "Transaction-Table"


    # Update balance in fastag table
def update_fastag_balance(tag_id, vehicle_id, updated_balance):
    # try: 
        database = client.get_database_client(DATABASE_NAME)
        fastag_container = database.get_container_client(FASTAG_CONTAINER)

        operations = [
            {"op": "replace", "path" : "/balance", "value": updated_balance}
        ]

        response = fastag_container.patch_item(
            item = tag_id,
            patch_operations = operations,
            partition_key = vehicle_id
        )
        logging.warn("Fastag balance updated")
    # except (Exception,exceptions.CosmosHttpResponseError) as e:
    #     raise Exception("Internal server error")
    


    # Create new transaction in transaction table
def create_transaction(tag_id, type, amount, description):
    # try:
        if type == 'debit' or type == 'credit':
            database = client.get_database_client(DATABASE_NAME)
            transaction_container = database.get_container_client(TRANSACTION_CONTAINER)

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            response = transaction_container.create_item({
                "timestamp" : timestamp,
                "tagId" : tag_id,
                "type" : type,
                "amount" : amount,
                "description" : description
            }, enable_automatic_id_generation=True)

            return True
        else:
            return False

    # except (Exception,exceptions.CosmosHttpResponseError) as e:
    #     return func.HttpResponse(
    #         body=json.dumps("Internal server error"),
    #         status_code=500
    #     )