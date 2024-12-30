from utils.db_connection import challan_container
from models.challan_model import Challan
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
            "date": challan.creation_time,
            "due_time": challan.due_time,
            "status": challan.status,
            "settlement_date": challan.settlement_time
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
        
    def get_unsettled_overdue_challans(self):
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
            item = challan.id,
            patch_operations=operations,
            partition_key=vehicle_id
        )
        logging.warn("Paid a challan")
        
    def pay_all_challans(self, unsettled_challan_ids, vehicle_id):
        settlement_time = time.time()
        operations = [
            {"op":"replace", "path":"/status", "value": "settled"},
            {"op":"replace", "path":"/settlement_date", "value": settlement_time}
        ]
        for id in unsettled_challan_ids:
            challan_container.patch_item(
                item = id,
                patch_operations=operations,
                partition_key=vehicle_id
            )
        logging.warn("Paid all challans")    

    def settle_all_overdue_challans(self, unsettled_overdue_challan_ids, vehicle_id):
        settlement_time = time.time()
        operations = [
            {"op":"replace", "path":"/status", "value": "settled"},
            {"op":"replace", "path":"/settlement_date", "value": settlement_time}
        ]
        for id in unsettled_overdue_challan_ids:
            challan_container.patch_item(
                item = id,
                patch_operations=operations,
                partition_key=vehicle_id
            )
        logging.warn("Settled all overdue challans")
        