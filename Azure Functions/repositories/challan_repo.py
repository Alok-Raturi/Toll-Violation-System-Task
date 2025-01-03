from database.connection import challan_container
from database.models import Challan
import time
import logging

class ChallanRepo:
    def __init__(self):
        pass
    
    def create_challan(self, challan: Challan):
        # Creating new challan in challan table
        challan_container.create_item({
            "vehicleId": challan.vehicle_id,
            "amount": challan.amount,
            "location": challan.location,
            "description": challan.description,
            "date": challan.date,
            "due_time": challan.due_time,
            "status": challan.status,
            "settlement_date": challan.settlement_date
        }, enable_automatic_id_generation=True
        )

    def get_all_challans(self, vehicle_id):
        query = "SELECT * FROM c WHERE c.vehicleId = @vehicleId"
        items = list(challan_container.query_items(
            query=query,
            parameters=[
                {"name": "@vehicleId", "value": vehicle_id},
            ],
            enable_cross_partition_query=True
        )) 
        return items
        
    def get_unsettled_overdue_challans(self, vehicle_id):
        current_time = time.time()
        query = '''SELECT *
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
        return items

    def pay_a_challan(self, challan_id, vehicle_id):
        settlement_time = time.time()
        operations = [
            {"op":"replace", "path":"/status", "value": "settled"},
            {"op":"replace", "path":"/settlement_date", "value": settlement_time}
        ]
        challan_container.patch_item(
            item = challan_id,
            patch_operations=operations,
            partition_key=vehicle_id
        )
        logging.warning("Paid a challan")
        

    def settle_all_overdue_challans(self, unsettled_overdue_challans, vehicle_id):
        settlement_time = time.time()
        operations = [
            {"op":"replace", "path":"/status", "value": "settled"},
            {"op":"replace", "path":"/settlement_date", "value": settlement_time}
        ]
        
        for challan in unsettled_overdue_challans:
            challan_container.patch_item(
                item = challan.id,
                patch_operations=operations,
                partition_key=vehicle_id
            )
        logging.warning("Settled all overdue challans")
        
    def does_challan_exist(self, id):
        query = "SELECT * FROM c WHERE c.id = @id"
        items = list(challan_container.query_items(
            query=query,
            parameters=[
                {"name":"@id", "value":id}
            ],
            enable_cross_partition_query=True
        ))
        return items
    
    def get_all_unsettled_challan(self,vehicle_id):
        query = "SELECT * FROM c WHERE c.vehicleId = @vehicleId AND c.status = 'unsettled'"
        items = list(challan_container.query_items(
            query=query,
            parameters=[
                {"name": "@vehicleId", "value": vehicle_id},
            ],
            enable_cross_partition_query=True
        )) 
        return items
    