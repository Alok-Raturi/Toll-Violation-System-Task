from repositories.transaction_repo import TransactionRepo
from models.transaction_model import Transaction
class TransactionService:
    def __init__(self):
        self.transaction_repo = TransactionRepo()
    def create_transaction(self):
        # All the checks
        self.transaction_repo.create_transaction()