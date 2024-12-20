from utils.db_connection import client
from azure.cosmos import  exceptions
from utils.transactions import create_transaction, update_fastag_balance
import datetime
import time
import logging


DATABASE_NAME = "Toll-Violation-Detection-System-DB"
USER_CONTAINER = "User-Table"
VEHICLE_CONTAINER = "Vehicle-Table"
CHALLAN_CONTAINER = "Challan-Table"
FASTAG_CONTAINER = "Fastag-Table"
TRANSACTION_CONTAINER = "Transaction-Table"



# Settle overdue challans
def settle_overdue_challans(challans, vehicle_id, tag_id, updated_balance):
    try:
        settlement_time = str(datetime.datetime.now())
        operations = [
            {"op":"replace", "path":"/status", "value": "settled"},
            {"op":"replace", "path":"/settlement_time", "value": settlement_time}
        ]
        for challan in challans:
            # Update challan table with settled status and settlement time
            response = challan_container.patch_item(
                item = challan["id"],
                patch_operations = operations,
                partition_key = vehicle_id
            )
            
            # Update transaction table    
            create_transaction(tag_id, 'debit', challan["amount"], "Forced Challan Payment")

        update_fastag_balance(tag_id, vehicle_id, updated_balance)
        return True    
    except:
        return False    


def total_overdue_challans(challans):
    total = 0

    for challan in challans:
        total = total + challan["amount"]
    return total    


def fetch_overdue_challan(vehicle_id):
    try:
        database = client.get_database_client(DATABASE_NAME)
        challan_container = database.get_container_client(CHALLAN_CONTAINER)
        current_time = time.time()
        logging.warn(current_time)

        query = '''SELECT c.id, c.amount 
                   FROM c 
                   WHERE c.vehicleId = @vehicleId 
                   AND c.status = 'unsettled' 
                   AND @currentTime > c.due_time  '''

        items = list(challan_container.query_items(
            query=query,
            parameters=[
                {"name": "@vehicleId", "value": vehicle_id},
                {"name": "@currentTime", "value": current_time}
            ],
            enable_cross_partition_query=True
        ))
        logging.warn(items)
        return items
    except:
        return False