from database.connection import vehicle_container
from database.models import Vehicle
import logging

class VehicleRepo:
    def __init__(self):
        pass

    def create_vehicle(self, vehicle: Vehicle):
        vehicle_container.create_item({
            "id": vehicle.id,
            "email": vehicle.email,
            "tagId": vehicle.tag_id
        })
        logging.warning("Vehicle Created")

    def get_vehicles(self, email):
        query = "SELECT * FROM c WHERE c.email = @email"
        items = list(vehicle_container.query_items(
            query=query,
            parameters=[
                {"name":"@email","value":email}
            ],
            enable_cross_partition_query=True
        ))
        return items

    def issue_fastag(self, tag_id, vehicle_id, email):
        # Adding fastag in vehicle table
        operations = [
            {"op":"replace", "path":"/tagId", "value": tag_id}
        ]
        vehicle_container.patch_item(
            item = vehicle_id,
            patch_operations=operations,
            partition_key=email
        )
        
    def does_vehicle_exists(self, vehicle_id):
        query = "SELECT c.email, c.tagId FROM c WHERE c.id = @vid"
        items = list(vehicle_container.query_items(
            query=query,
            parameters=[
                {"name":"@vid","value":vehicle_id}
            ],
            enable_cross_partition_query=True
        ))
        return items

    def check_associated_email_with_vehicle(self,vehicle_id, email):
        query = 'Select * from c where c.id = @vehicleId and c.email=@email'
        check_vehicle_association = list(vehicle_container.query_items(query=query,
                                                                       parameters=[
                                                                           {"name":"@vehicleId","value":vehicle_id},
                                                                           {"name":"@email","value":email}
                                                                       ],
                                                                       enable_cross_partition_query=True))
        return len(check_vehicle_association)

    