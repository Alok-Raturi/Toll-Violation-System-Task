from repositories.user_repo import UserRepo
from database.models import User
from helper.send_email import send_email
from utils.jwt_decode import encode_token
import azure.functions as func
import logging
import json
from database.models import LoginModel

USER_CREATED_SUBJECT = "You are successfully registered"
USER_CREATED_BODY = """
Thank you for registering with us. You are successfully registered with us.<br>
Your login credentials are:<br>
    &nbsp;Email: {0}<br>
    &nbsp;Password: {1}<br>
You are designated as a {2}.<br>
Please login to the system to access the services.
"""


class UserService:
    def __init__(self):
        self.user_repo = UserRepo()

    def create_user(self, user: User):
        if self.user_repo.does_user_exists(user.email):
            logging.error("User already exists")
            return func.HttpResponse(
                json.dumps("User already exists"),
                status_code = 404
            )

        self.user_repo.create_user(user) 
        logging.warning("User Created successfully")
        send_email(
            user.email, 
            USER_CREATED_SUBJECT, 
            USER_CREATED_BODY.format(
                user.email, 
                user.password, 
                user.designation
            )
        )

        return func.HttpResponse(
            json.dumps(f"Successfully created {user.designation} person"),
            status_code=201
        )

    def login(self,login_info:LoginModel):
        is_login = self.user_repo.login(login_info)
        if is_login == False:
            logging.error("Invalid email or password")
            return func.HttpResponse(
                json.dumps("Invalid email or password"),
                status_code = 404 
            )
        logging.warning("Login Successful")
        token = encode_token({
            "email" : login_info.email,
            "designation" : is_login[0]['designation'],
            "id" : is_login[0]['id']
        })
        logging.warning("Access Token generated")
        return func.HttpResponse(
            json.dumps({
                "access_token" : token
            }),
            status_code = 200
        )
