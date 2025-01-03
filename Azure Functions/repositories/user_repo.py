from database.connection import user_container
from database.models import User
from utils.password import hash_password, check_password
from database.models import LoginModel


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
        return len(items)
        
    def does_vehicle_owner_exists(self, email) -> bool:
        query = "SELECT * FROM c WHERE c.email = @email AND c.designation = 'user'"
        items = list(user_container.query_items(
            query=query,
            parameters=[
                {"name":"@email", "value":email}
            ]
        ))
        return len(items)
        
    def login(self, login_info: LoginModel):
        query = "SELECT * FROM c WHERE c.email = @email"
        items = list(user_container.query_items(
            query=query,
            parameters=[
                {"name":"@email", "value":login_info.email}
            ]
        ))   
        if len(items) == 0 or not check_password(login_info.password, items[0]['password']):
            return False
        else:
            return items