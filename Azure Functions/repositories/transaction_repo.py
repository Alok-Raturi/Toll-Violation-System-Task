from utils.db_connection import transaction_container
from models.transaction_model import Transaction
import logging
import datetime
import pytz

class TransactionRepo:
    def __init__(self):
        pass

    def create_transaction(transaction: Transaction):
        # Create a transaction in transaction table
        timestamp = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
            
        transaction_container.create_item({
            "timestamp" : timestamp,
            "tagId" : transaction.tag_id,
            "type" : transaction.type,
            "amount" : transaction.amount,
            "description" : transaction.description,
            "location": transaction.location
        }, enable_automatic_id_generation=True)
        logging.warn("Transaction created") 

    def get_transaction_history(self, tag_id):
        query = "SELECT * FROM c WHERE c.id = @tagId"
        items = transaction_container.query_items(
            query=query,
            parameters=[
                {"name":"@tagId","value":tag_id}
            ],
            enable_cross_partition_query=True
        )    
        return items