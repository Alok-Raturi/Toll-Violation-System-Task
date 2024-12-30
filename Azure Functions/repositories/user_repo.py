# Class to communicate with user container
from utils.db_connection import user_container
from models.user_model import User
from utils.password import hash_password

class UserRepo:
    def __init__(self):
        pass
    
    def create_user(self, user: User):
        hashed_password = hash_password(user.password)
        user_container.create_item({
            "name": user.name,
            "designation": user.designation,
            "password": hashed_password,
            "email": user.email
        }, enable_automatic_id_generation=True
        )

    def does_user_exists(self, email) -> bool:
        query = "SELECT * FROM c WHERE c.email = @email"
        items = list(user_container.query_items(
            query=query,
            parameters=[
                {"name":"@email", "value":email}
            ]
        ))
        if len(items) == 0:
            # User doesn't exists
            return False
        else:
            # User already exists
            return True
        
    def does_vehicle_owner_exists(self, email) -> bool:
        query = "SELECT * FROM c WHERE c.email = @email AND c.designation = 'user'"
        items = list(user_container.query_items(
            query=query,
            parameters=[
                {"name":"@email", "value":email}
            ]
        ))
        if len(items) == 0:
            # Owner doesn't exists
            return False
        else:
            # Owner already exists
            return True    