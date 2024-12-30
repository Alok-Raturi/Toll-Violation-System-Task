from utils.db_connection import fastag_container
from models.fastag_model import Fastag
import logging

class FastagRepo:
    def __init__(self):
        pass
        
    def create_fastag(self, fastag: Fastag):
        fastag_container.create_item({
            "id": fastag.id,
            "balance": fastag.balance,
            "status": fastag.status,
            "vehicleId": fastag.vehicle_id,
            "email": fastag.email
        })

    def does_fastag_exists(self, tag_id):
        query = "SELECT * FROM c WHERE c.id = @tagId"
        items = list(fastag_container.query_items(
            query=query,
            parameters=[
                {"name":"@tagId", "value":tag_id}
            ],
            enable_cross_partition_query=True
        ))
        if len(items) == 0:
            return False
        else: 
            return True

    def get_status(self, tag_id):
        query = "SELECT c.status FROM c WHERE c.id = @tagId"
        items = list(fastag_container.query_items(
            query=query,
            parameters=[
                {"name": "@tagId", "value": tag_id}
            ],
            enable_cross_partition_query=True
        ))
        return items

    def get_balance(self, tag_id):
        query = "SELECT c.balance FROM c WHERE c.id = @tagId"
        items = list(fastag_container.query_items(
            query=query,
            parameters=[
                {"name": "@tagId", "value": tag_id}
            ],
            enable_cross_partition_query=True
        ))
        return items

    def set_balance(self, fastag: Fastag, new_balance, vehicle_id):
        operations = [
            {"op": "replace", "path" : "/balance", "value": new_balance}
        ]
        response = fastag_container.patch_item(
            item = fastag.id,
            patch_operations = operations,
            partition_key = vehicle_id
        )
        logging.warning("Fastag balance updated")

    def change_status(self, fastag: Fastag, new_status, vehicle_id):
        operations = [
            {"op": "replace", "path": "/status", "value": new_status}
        ]
        fastag_container.patch_item(
            item=fastag.id,
            patch_operations = operations,
            partition_key = vehicle_id
        )
        logging.warn("Fastag blacklisted")