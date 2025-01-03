from database.connection import transaction_container
from database.models import Transaction
import logging

class TransactionRepo:
    def __init__(self):
        pass

    def create_transaction(self,transaction: Transaction):   
        transaction_container.create_item({
            "timestamp" : transaction.timestamp,
            "tagId" : transaction.tag_id,
            "type" : transaction.type,
            "amount" : transaction.amount,
            "description" : transaction.description,
            "location": transaction.location
        }, enable_automatic_id_generation=True)
        logging.warn("Transaction created") 

    def get_transaction_history(self, tag_id):
        query = "SELECT * FROM c WHERE c.tagId = @tagId"
        items = list(transaction_container.query_items(
            query=query,
            parameters=[
                {"name":"@tagId","value":tag_id}
            ],
            enable_cross_partition_query=True
        ))    
        return items