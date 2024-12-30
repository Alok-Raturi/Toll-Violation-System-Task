from repositories.user_repo import UserRepo
from models.user_model import User
from utils.password import check_password_strength, PASSWORD_CONSTRAINT
from utils.send_email import send_email
from email_validator import validate_email
import azure.functions as func
import logging
import json

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
        # Email validation
        validate_email(user.email)
        # Password strength validtion
        if not check_password_strength(user.password):
            logging.error("Password Constraint")
            return func.HttpResponse(
                json.dumps(PASSWORD_CONSTRAINT),
                status_code=404
            )
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


