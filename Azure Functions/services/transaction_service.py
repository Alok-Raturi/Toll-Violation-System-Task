import azure.functions as func
from repositories.transaction_repo import TransactionRepo
from repositories.fastag_repo import FastagRepo
from database.models import Transaction
import json
import logging
class TransactionService:
    def __init__(self):
        self.transaction_repo = TransactionRepo()
    def create_transaction(self):
        # All the checks
        self.transaction_repo.create_transaction()

    def get_history(self, tag_id):
        fastag_repo = FastagRepo()
        if not fastag_repo.does_fastag_exists(tag_id):
            logging.error("No fastag with this id")
            return func.HttpResponse(
                json.dumps("No fastag with this id"),
                status_code = 404
            )
        
        history = self.transaction_repo.get_transaction_history(tag_id=tag_id)
        if not history:
            logging.error("No transaction history")
            return func.HttpResponse(
                json.dumps("No transaction history"),
                status_code = 404
            )
        return func.HttpResponse(
            json.dumps(history),
            status_code = 200
        )
        